# 🚀 [Tips Hindawi](https://www.tipshindawi.com/) Internship (August–October) 2026

> 🎓 This project was built during the [ **Tips Hindawi** ](https://www.tipshindawi.com/) **Internship (August–October) 2026**.

## 👤 Participant

| Field            | Value                                |
| ---------------- | ------------------------------------ |
| Full Name        | Toka Tarek Kamal                                     |
| Project Name     | AI Project Planner                                     |
| GitHub Username  | toqa8                                     |
| Internship Batch | August–October 2026                  |
| Training Program | Large Language Models (LLMs) Program |
| Organization     | [**Edrak for Ai**](https://edrak4ai.com/en)                         |

---

# 📖 Project Overview

AI Project Planner is an AI-based tool that generates organized project plans based on project specifications. Users can upload a project PDF and provide details such as team size and project duration. The application then generates a plan that includes the required skills, tasks, team roles, and timeline.

---

# ✨ Features

* Generate project plans based on uploaded project PDF and user inputs.
* Identify the skills required for the project.
* Break the project into tasks.
* Suggest team roles and assign tasks.
* Create a project timeline.
* Provide an easy-to-use interface with Streamlit.

---

# 🛠️ Technologies Used

* Python
* LangChain
* LLMs
* Pydantic
* Kaggle GPU (T4)
* Ngrok
* Streamlit

---

# ⚙️ Installation

1. Open the [Kaggle Notebook](https://www.kaggle.com/code/toqatareq/tips-hindawi-l5-ngrok-the-gpu-session), enable the GPU (T4), and run the notebook to load the model and start the API.
2. Clone the repository
3. Install the required libraries:
   ```bash
   pip install -r requirements.txt
   ```
4. Set up the required environment variables in your `.env` file.
5. Open the project in VS Code and run:
   ```bash
   streamlit run app.py
   ```     

---

# 🚀 Usage

1. Upload the project description PDF.
2. Enter the number of team members and the project duration.
3. Click the the generate button to create the project plan.

---

# 📸 Demo

![image_alt](https://github.com/toqa8/AI-Project-Planner/blob/c5f6e2900831bdc8732c91b31e8d0f5f8496ffac/1.PNG)
![image_alt](https://github.com/toqa8/AI-Project-Planner/blob/8bb10fdbb0607602cf17e07159d8c58659c39b1a/2.PNG)
![image_alt](https://github.com/toqa8/AI-Project-Planner/blob/a28eb75f562a896dc80e2cc7a6e561041daa7fac/3.PNG)
![image_alt](https://github.com/toqa8/AI-Project-Planner/blob/acb3591b18c657c692efa4881e6d5a1b5dce6d80/4.PNG)
![image_alt](https://github.com/toqa8/AI-Project-Planner/blob/d58e7e0bd70ddad786cf077662d3a4c90cddc975/5.PNG)

---

# 📈 Results

- Generates a clear and structured plan for the user's project.
- Provides an easy-to-use interface.

---

# 🔮 Future Improvements

* Reduce response time to make project plan generation faster.
Improve the quality and accuracy of generated project plans.
Improve task assignment and timeline estimation.
Deploy the model API on a more stable hosting service to reduce dependence on temporary Kaggle sessions.
- **Automatic retries:** Re-run a chain when the model returns invalid JSON, instead of showing an error to the user.
- **Input-aware validation:** Check that the number of generated team members matches the requested team size, and that the timeline fits within the project duration.
- **Guaranteed structured output:** Use constrained decoding (e.g., Outlines) on the model server so the output always matches the Pydantic schemas.
- **Permanent model hosting:** Replace the temporary Ngrok tunnel with a stable deployment, so the API URL does not change between sessions.
- **Better retrieval:** Combine dense search with keyword search (BM25) and add reranking to improve the context passed to each chain.
- **More input formats:** Support DOCX and scanned PDFs (OCR), and allow multiple files per project.
- **Editable plans:** Let users edit tasks, roles, and the timeline in the UI, and regenerate a single section without rerunning the whole pipeline.
- **Timeline visualization:** Display the timeline as a Gantt chart.
- **Export options:** Download the final plan as PDF or Markdown.
- **Testing and evaluation:** Add unit tests for the schemas and helper functions, and evaluate plan quality on a set of sample project briefs.

---

# 📚 About the Internship

This project was developed as part of the [**Tips Hindawi**](https://www.tipshindawi.com/) **Internship (August–October) 2026**, and it will be showcased on the official [Tips Hindawi](https://www.tipshindawi.com/) website.

[Tips Hindawi](https://www.tipshindawi.com/) is the internships department of [**Edrak for Ai**](https://edrak4ai.com/en), and the internship encourages participants to build real-world projects, apply practical skills, and showcase their work through GitHub.

For more information about the internship, training programs, and upcoming batches, visit the official [Tips Hindawi](https://www.tipshindawi.com/) website.

---

# 📄 License

This project is shared for educational and portfolio purposes.
