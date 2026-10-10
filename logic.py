# Loads PDF files and extracts their text.
from langchain_community.document_loaders import PyPDFLoader

# RecursiveCharacterTextSplitter splits long text into smaller chunks.
# It tries to split the text at natural boundaries, such as paragraphs,
# then lines, then words, and finally characters if needed.
# This helps keep related information together instead of cutting the text
# at arbitrary positions, which is useful for semantic search and embeddings.
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Stores document embeddings and supports similarity-based search.
from langchain_community.vectorstores import FAISS

# Converts text into numerical embeddings using a Hugging Face model.
from langchain_huggingface import HuggingFaceEmbeddings

# Base class used to connect our external model API to LangChain.
from langchain_core.language_models.llms import LLM

# Creates prompts containing instructions and input variables.
from langchain_core.prompts import PromptTemplate

# PydanticOutputParser converts the LLM's answer into structured data
from langchain_core.output_parsers import PydanticOutputParser

# Imports Any and List so we can specify what types of values our variables, functions, and lists can contain.
from typing import Any, List

# Defines data schemas and validates generated output.
from pydantic import BaseModel, Field, field_validator, model_validator

# Sends HTTP requests to the external model API.
import requests

import os
from dotenv import load_dotenv

# Load environment variables from a .env file.
load_dotenv()


# ===============
# Loading the PDF
# ===============

def load_pdf(pdf_path):

    loader = PyPDFLoader(pdf_path)
    
    # Read the PDF and return its pages as Document objects.
    # Each document contains page text and metadata.
    documents = loader.load()

    return documents


# ==========
# Chunking
# ==========

def create_chunks(documents):

    # Splits the PDF into smaller text chunks.
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100
    )

    # Split the documents while preserving their associated metadata.
    chunks = text_splitter.split_documents(documents)

    return chunks


# =====================
# Search system
# =====================

embedding_model_name = "sentence-transformers/all-MiniLM-L6-v2"

embedding = HuggingFaceEmbeddings(
    model_name=embedding_model_name
)


def create_search_systems(chunks):

    # Creates a FAISS vector database for semantic (dense) search.
    vectordb = FAISS.from_documents(
        chunks,
        embedding
    )

    return vectordb


def dense_search(query, vectordb, k=3):

    # Retrieves the top k chunks that are most relevant
    # to the current task using semantic similarity.
    results = vectordb.similarity_search(
        query,
        k=k
    )

    return results


# =================
# Hugging Face API
# =================

# The Ngrok URL that exposes our FastAPI model endpoint.
URL = os.getenv("MODEL_API_URL")

# The API key used to access the model.
headers = {
    "Authorization": f"Bearer {os.getenv('MODEL_API_KEY')}"
}


def generate_text(prompt, max_length=500):

    # Sends the prompt to the Hugging Face llm through the API.
    payload = {
        "prompt": prompt,
        "max_length": max_length
    }

    response = requests.post(
        URL,
        headers=headers,
        json=payload
    )

    # Gets the generated response from the API.
    # This assumes the API response contains a "response" field.
    return response.json()["response"]


# ================================
# WRAP THE API AS A LANGCHAIN LLM
# ================================

# This wrapper allows LangChain to call our external model
# as if it were a regular LangChain language model.
class CustomHFLLM(LLM):

    # Receives the prompt from LangChain and sends it
    # to the Hugging Face model to generate a response.
    def _call(self, prompt: str, stop: Any = None) -> str:

        # Send the prompt to the external API and return its output.
        return generate_text(prompt)

    @property
    def _llm_type(self) -> str:
        return "custom_huggingface_api"


# Creates an instance of our custom LLM.
# This allows us to use the Hugging Face model inside LangChain chains.
llm = CustomHFLLM()


# ==========================================
# Pydantic schemas for the chains' outputs
# ==========================================

# Pydantic schemas define the expected structure of the LLM's answer,
# including the required fields and their data types.

# ----------------------------
# Chain 2 (Skills) output
# ----------------------------

class SkillsOutput(BaseModel):

    # The output must contain a list of skill names.
    skills: list[str] = Field(
        description="a list of Technical skills and technologies needed."  # This description is included in the skills chain prompt through the parser's format instructions.
    )

    @field_validator("skills")
    @classmethod
    def clean_skills(cls, v):
        # Remove extra spaces, empty values, and duplicate skills.
        # Duplicate detection ignores differences in letter casing.
        seen, result = set(), []
        for item in v:
            item = item.strip()
            if item and item.lower() not in seen:
                seen.add(item.lower())
                result.append(item)
                
        # Reject the output if no valid skills remain.        
        if not result:
            raise ValueError("skills list is empty")
        
        return result


# ----------------------------
# Chain 3 (Task) output
# ----------------------------

class Task(BaseModel):

    title: str = Field(description="Short task title.")
    description: str = Field(description="One or two sentences describing the task.")


class TasksOutput(BaseModel):

    tasks: list[Task] = Field(
        description="Main project tasks, in logical order."
    )

    @field_validator("tasks")
    @classmethod
    def check_tasks(cls, v):
        
        # Reject an empty task list.
        if not v:
            raise ValueError("tasks list is empty")
        
        return v


# ----------------------------
# Chain 4 (Team roles) output
# ----------------------------

class TeamMember(BaseModel):

    role: str = Field(
        description="A descriptive role name based on the assigned tasks (not just a number)."
    )
    assigned_tasks: list[str] = Field(
        description="Titles of the tasks this member handles."
    )

    @field_validator("role")
    @classmethod
    def check_role(cls, v):
        
        # Removes extra spaces from the beginning and end of the role name.
        v = v.strip()
        
        # Reject empty role names or names consisting only of digits.
        if not v or v.isdigit():
            raise ValueError("role must be a descriptive name, not a number")
        
        return v


class TeamOutput(BaseModel):

    # The model must return a non-empty list of team members.
    members: list[TeamMember]

    @field_validator("members")
    @classmethod
    def check_members(cls, v):

        # Reject an empty team list.
        if not v:
            raise ValueError("members list is empty")

        return v


# ----------------------------
# Chain 5 (Timeline) output
# ----------------------------

class TimelineEntry(BaseModel):

    start_week: int = Field(ge=1, description="First week of this period.")
    end_week: int = Field(ge=1, description="Last week of this period.")
    tasks: list[str] = Field(description="Task titles worked on during this period.")

    @model_validator(mode="after")
    def check_weeks(self):
        # Ensure that the period ends on or after its starting week.
        if self.end_week < self.start_week:
            raise ValueError("end_week must be >= start_week")
        return self


class TimelineOutput(BaseModel):

    entries: list[TimelineEntry]


# =======================
# CREATE OUTPUT PARSERS
# =======================

# PydanticOutputParser converts (parses)
# the LLM's response into the corresponding Pydantic object.

skills_parser = PydanticOutputParser(pydantic_object=SkillsOutput)
tasks_parser = PydanticOutputParser(pydantic_object=TasksOutput)
roles_parser = PydanticOutputParser(pydantic_object=TeamOutput)
timeline_parser = PydanticOutputParser(pydantic_object=TimelineOutput)


# =======
# Prompts
# =======

description_prompt = PromptTemplate(
    input_variables=["context"],
    template="""
    Analyze the following project information and explain clearly
    what the project is about to clarify the idea to the user.
    Don't talk about the requirement details, just give an understandable overview of the project idea.

    Context:
    {context}

    Give a short and simple description.
    Focus only on information supported by the context.

    The description must be a paragraph of no more than 300 words.
    """
)


skills_prompt = PromptTemplate(
    input_variables=["description", "context"],
    partial_variables={
        "format_instructions": skills_parser.get_format_instructions()
    },
    template="""
    You are a project planning assistant.

    Identify the technical skills and technologies needed for
    the project.

    Project understanding:
    {description}

    Relevant project information:
    {context}

    Rules:
    - Use the project information as the main source.
    - If a technology is explicitly specified, include it.
    - If no specific technology is specified, suggest only a few
      relevant technology options. such as if the programming language is not specified, suggest a few relevant programming languages, like: "programming language options: Python, JavaScript, Java".
    - Do not include testing skills, documentation skills, or soft skills.
    - Do not suggest unrelated technologies.
    - Do not suggest cloud platforms, machine learning, or
      predictive maintenance unless they are explicitly required
      by the project.
    - Do not include explanations.
    - Do not repeat any word or technology unnecessarily.
    - Do not include "Assistant:" or "Human:".
    - return a short list.
    - each skill must be a simple string.
    - don't invent unrelated technologies.
    
    return ONLY a JSON object, with no text before or after it.

    Use options if the project does not specify a technology, but do not invent unrelated technologies.
    
    {format_instructions}
    """
)


tasks_prompt = PromptTemplate(
    input_variables=["description", "skills", "context"],
    partial_variables={
        "format_instructions": tasks_parser.get_format_instructions()
    },
    template="""
    Based on the project understanding, required skills, and
    project information, break the project into the main tasks
    that need to be completed. Don't include the documentation or testing tasks, just the main tasks that are needed to implement the project.

    Project understanding:
    {description}

    Skills and technology options:
    {skills}

    Project information:
    {context}

    Return the tasks in a logical order.
    Each task has a title and a description of the task.

    Do not add tasks that are unrelated to the project.
    
    Do not include the documentation or testing tasks, just the main tasks that are needed to implement the project.

    Return ONLY a JSON object, with no text before or after it.
    
    {format_instructions}
    """
)


roles_prompt = PromptTemplate(
    input_variables=["tasks", "team_size"],
    partial_variables={
        "format_instructions": roles_parser.get_format_instructions()
    },
    template="""
    You are a project planning assistant.

Assign the project tasks to team members based on the tasks below.

Tasks:
{tasks}

Number of team members:
{team_size}

Rules:
- Create exactly {team_size} team members.
- Give each member the tasks they should handle.
- a task can be assigned to multiple members if needed.
- a member can have multiple tasks.
- Base the roles on the provided tasks.
- Do not assign the documentation or testing tasks to any member, just the main tasks that are needed to implement the project.
- Do not create new tasks.
- Do not use only numbers as roles.
- Use only the task titles in the assigned tasks.
- Do not include explanations.
- Do not include "Assistant:" or "Human:".
    
{format_instructions}    
    """
)


timeline_prompt = PromptTemplate(
    input_variables=["tasks", "roles", "duration", "context"],
    partial_variables={
        "format_instructions": timeline_parser.get_format_instructions()
    },
    template="""
    You are a project planning assistant.

Create a realistic timeline for completing the project.

Tasks:
{tasks}

Team roles:
{roles}

Project duration:
{duration}

Relevant project information:
{context}

Rules:
- Organize the tasks into logical stages.
- Tasks may overlap when appropriate.
- Consider project milestones mentioned in the project information.
- Do not invent unrelated tasks.
- The timeline MUST fit completely within the given project duration.
- Do NOT use any week after the given duration.
- Start from Week 1.
- The final week MUST be the given duration.
- Assign every important task to one or more time periods.
- Related tasks can overlap when appropriate.
- Keep the order of dependent tasks logical.
- Use project milestones or phases mentioned in the project information when relevant.
- Do not include explanations.
- Do not include "Assistant:" or "Human:".

{format_instructions}    
    """
)


# =======
# Chains
# =======

description_chain = description_prompt | llm
skills_chain = skills_prompt | llm | skills_parser
tasks_chain = tasks_prompt | llm | tasks_parser
roles_chain = roles_prompt | llm | roles_parser
timeline_chain = timeline_prompt | llm | timeline_parser


# =================
# Pydantic schema
# =================

# Defines the structure of the final project plan.
# Pydantic validates that the final output contains
# the required fields and correct data types.

class ProjectPlan(BaseModel):

    description: str
    required_skills: list[str]
    tasks: list[str]
    team_roles: list[str]
    timeline: list[str]


# ===================================
# Convert structured output to text
# ===================================

# The parsed Pydantic objects are converted back to text
# so they can be passed to the next prompt (chain).

def skills_to_text(skills_output):

    return "\n".join(skills_output.skills)


def tasks_to_text(tasks_output):

    return "\n".join(
        f"{i}. {task.title}: {task.description}"
        for i, task in enumerate(tasks_output.tasks, start=1)
    )


def roles_to_text(roles_output):

    return "\n".join(
        f"{i}. {member.role}: {', '.join(member.assigned_tasks)}"
        for i, member in enumerate(roles_output.members, start=1)
    )


# =============================
# BUILD THE FINAL PROJECT PLAN
# =============================

def create_project_plan(description, skills, tasks, roles, timeline):

    # Extract the Python list of skills from SkillsOutput.
    # The first "skills" refers to the object, and the second "skills" refers to the list stored inside it.
    skills = skills.skills

    # Combines each task's title and description into one readable string.
    tasks = [
        f"{task.title}: {task.description}"
        for task in tasks.tasks
    ]

    # Combines each team member's role with their assigned tasks into one readable string.
    roles = [
        f"{member.role}: {', '.join(member.assigned_tasks)}"
        for member in roles.members
    ]

    # Sorts timeline entries
    entries = sorted(timeline.entries, key=lambda e: e.start_week)

    # Converts each timeline entry into a readable string showing its week or week range and tasks.
    timeline = []
    for e in entries:
        if e.start_week == e.end_week:
            weeks = f"Week {e.start_week}"
        else:
            weeks = f"Week {e.start_week}-{e.end_week}"

        timeline.append(f"{weeks}: {', '.join(e.tasks)}")
        

    # Creates and validates the final project plan using Pydantic.
    project_plan = ProjectPlan(
        description=description,
        required_skills=skills,
        tasks=tasks,
        team_roles=roles,
        timeline=timeline
    )

    return project_plan


# ===========================================
# MAIN FUNCTION: RUN THE COMPLETE PIPELINE
# ===========================================

def generate_project_plan(pdf_path, team_size, duration):

    # Convert user-provided values into integers.
    team_size = int(team_size)
    duration = int(duration)

    # 1. Load the project PDF and extract its content.
    documents = load_pdf(pdf_path)

    # 2. Split the extracted text into smaller chunks.
    chunks = create_chunks(documents)

    # 3. Embed the chunks and create the FAISS database.
    vectordb = create_search_systems(chunks)


    # -----------------------------------------------------------
    # Step 4: Retrieves chunks related to the main project idea.
    # -----------------------------------------------------------

    description_docs = dense_search(
        "project purpose objectives main idea features requirements",
        vectordb,
        k=3
    )

    # Combine the retrieved chunk text into one context string.
    description_context = "\n\n".join(
        doc.page_content for doc in description_docs
    )


    # ---------------------------
    # Step 5: Run Description Chain
    # ---------------------------

    description = description_chain.invoke(
        {"context": description_context}
    ).strip()  # removes extra whitespace from the beginning and end.


    # -------------------------------------------
    # Step 6: Retrieves chunks related to skills
    # -------------------------------------------

    skills_docs = dense_search(
        "technologies tools programming languages frameworks technical requirements skills",
        vectordb,
        k=3
    )

    skills_context = "\n\n".join(
        doc.page_content for doc in skills_docs
    )


    # -------------------------
    # Step 7: Run Skills Chain
    # -------------------------

    # Uses the project understanding from Chain 1
    # together with the relevant retrieved context.
    skills = skills_chain.invoke({
        "description": description,
        "context": skills_context
    })


    # -------------------------------------------
    # Step 8: Retrieves chunks related to tasks
    # -------------------------------------------
    
    tasks_docs = dense_search(
        "project features components functionality implementation development tasks",
        vectordb,
        k=3
    )

    tasks_context = "\n\n".join(
        doc.page_content for doc in tasks_docs
    )


    # ------------------------
    # Step 9: Run Tasks Chain
    # ------------------------

    # Uses the outputs from the previous chains
    # together with the relevant retrieved context.
    tasks = tasks_chain.invoke({
        "description": description,
        "skills": skills_to_text(skills),
        "context": tasks_context
    })


    # -------------------------
    # Step 10: Run Roles Chain
    # -------------------------

    # Uses the previous chains outputs and the user-provided team size.
    roles = roles_chain.invoke({
        "tasks": tasks_to_text(tasks),
        "team_size": team_size
    })


    # -----------------------------------------------
    # Step 11: Retrieves chunks related to timeline
    # -----------------------------------------------

    timeline_docs = dense_search(
        "project phases milestones dependencies schedule duration",
        vectordb,
        k=3
    )

    timeline_context = "\n\n".join(
        doc.page_content for doc in timeline_docs
    )


    # ----------------------------
    # Step 12: Run Timeline Chain
    # ----------------------------
    
    # Uses the generated tasks, roles, timeline and user-provided duration.
    timeline = timeline_chain.invoke({
        "tasks": tasks_to_text(tasks),
        "roles": roles_to_text(roles),
        "duration": duration,
        "context": timeline_context
    })


    # -----------------------------------
    # Step 13: Create final project plan
    # -----------------------------------

    # Combines all generated results into a structured
    # and validated Pydantic project plan.
    project_plan = create_project_plan(
        description,
        skills,
        tasks,
        roles,
        timeline
    )

    # Return the completed project plan to the calling code.
    return project_plan