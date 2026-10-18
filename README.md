<div align="center">

<table>
<tr>
<td width="38%" valign="middle" align="center">
<img src="assets/portrait.svg" width="300" alt="Halftone dot portrait of Adiel A Daniel"/>
</td>
<td width="62%" valign="middle" align="center">
<img src="assets/terminal.svg" width="500" alt="Terminal intro: whoami, cat about.txt, neofetch"/>
</td>
</tr>
</table>

<a href="https://linkedin.com/in/adieladaniel"><img src="assets/badges/linkedin.svg" alt="LinkedIn"/></a>
<a href="https://leetcode.com/adieladaniel"><img src="assets/badges/leetcode.svg" alt="LeetCode"/></a>
<a href="mailto:adieladaniel2006@gmail.com"><img src="assets/badges/gmail.svg" alt="Gmail"/></a>
<a href="https://adieladaniel.vercel.app/"><img src="assets/badges/portfolio.svg" alt="Portfolio"/></a>

<br/><br/>

<img src="assets/badges/open-to-ai-ml-engineer-genai-data.svg" alt="Open to AI/ML Engineer, GenAI, Data Scientist/Analyst roles"/>
<img src="https://komarev.com/ghpvc/?username=adieladaniel&label=Profile%20Views&color=8957e5&style=flat-square" alt="Profile views"/>

</div>

<br/>

## About

I'm a final-year B.Tech CSE (AI & ML) student in Bangalore, graduating in 2027. I build AI systems that do real work: LLM analytics pipelines, browser agents with human approval gates, and multimodal diagnostic models. Based in Bangalore, India, and open to relocation.

- **Edunext Technologies**, Software Engineer Intern, Apr to May 2026. Built an AI finance analytics platform as a LangGraph state-machine pipeline with rule-based and LLM-fallback routing, connected to Power BI dashboards. It runs on 10+ FastAPI endpoints over 50,000+ student fee records and cut manual reporting effort by 80% across 20+ client organizations.
- **IEEE Bangalore Section**, AI Intern, Apr to Jul 2025. Built OncoVision, a dual-output EfficientNetB0 that classifies eight cancer types and detects malignancy from histopathological images, at 97.99% and 98.13% accuracy.
- **Right now**, building MedReasonAI (an agentic multimodal diagnostic assistant) and sharpening RAG pipeline design.

<br/>

## My journey so far

<div align="center">
<img src="assets/journey.svg" width="100%" alt="Career timeline drawn as a git log graph, from starting B.Tech in Jul 2023 to building agentic AI now, graduating Apr 2027"/>
</div>

<br/>

## Featured work

<table width="100%">
<tr>
<td width="50%" valign="top">

### [OneForAll Agent](https://github.com/adieladaniel/OneForAll-Agent)
*Autonomous browser agent for multi-step business tasks*

- A runtime-enforced human approval gate and an independent verifier check every run
- Multi-user platform with roles, a PostgreSQL job queue with crash recovery, and a credential vault
- Load test: 280/280 runs passed ground truth, 0 cross-org leaks across 47,508 responses

<img src="assets/badges/python.svg" alt="Python"/> <img src="assets/badges/fastapi.svg" alt="FastAPI"/> <img src="assets/badges/postgresql.svg" alt="PostgreSQL"/> <img src="assets/badges/playwright.svg" alt="Playwright"/> <img src="assets/badges/gemini-api.svg" alt="Gemini API"/>

</td>
<td width="50%" valign="top">

### [MedReasonAI](https://github.com/adieladaniel/medreason-ai)
*Agentic multimodal diagnostic assistant*

- Fuses chest X-ray, lab values and radiology text
- Linked 53,000+ chest X-ray studies to clinical and lab records, and queried an 18GB+ lab-events dataset with DuckDB
- Fusing unimodal models (MIMIC-CXR DenseNet, ClinicalBERT) lifted macro F1 from 0.51 to 0.61, with SHAP and Grad-CAM explanations

<img src="assets/badges/pytorch.svg" alt="PyTorch"/> <img src="assets/badges/duckdb.svg" alt="DuckDB"/> <img src="assets/badges/clinicalbert.svg" alt="ClinicalBERT"/> <img src="assets/badges/shap.svg" alt="SHAP"/>

</td>
</tr>
<tr>
<td width="50%" valign="top">

### [FinnBot](https://github.com/adieladaniel/FinnBot-Financial-AI-Analytics-Engine)
*Hybrid analytics chatbot over your own data*

- Answers natural-language questions over uploaded or API-fetched data
- Rule-based query planning with a Gemini fallback for low-confidence questions
- Generates charts automatically

<img src="assets/badges/python.svg" alt="Python"/> <img src="assets/badges/fastapi.svg" alt="FastAPI"/> <img src="assets/badges/pandas.svg" alt="Pandas"/> <img src="assets/badges/gemini.svg" alt="Gemini"/>

</td>
<td width="50%" valign="top">

### [Obsidian RAG Assistant](https://github.com/adieladaniel/obsidian-rag-assistant)
*Local agentic RAG over an Obsidian vault*

- Answers questions about your notes with citations back to the source
- An agentic retrieval loop reformulates the query up to 3 times when the context is thin

<img src="assets/badges/python.svg" alt="Python"/> <img src="assets/badges/fastapi.svg" alt="FastAPI"/> <img src="assets/badges/ollama.svg" alt="Ollama"/> <img src="assets/badges/chromadb.svg" alt="ChromaDB"/> <img src="assets/badges/react.svg" alt="React"/>

</td>
</tr>
<tr>
<td width="50%" valign="top">

### [OncoVision](https://github.com/adieladaniel/OncoVision)
*Cancer classification and malignancy detection*

- Dual-output EfficientNetB0 on histopathological images: eight cancer types plus malignancy detection
- 97.99% classification accuracy and 98.13% malignancy detection
- Built as an AI Intern at IEEE Bangalore Section

<img src="assets/badges/python.svg" alt="Python"/> <img src="assets/badges/tensorflow.svg" alt="TensorFlow"/> <img src="assets/badges/opencv.svg" alt="OpenCV"/>

</td>
<td width="50%" valign="top">

### [PromptSense AI](https://github.com/adieladaniel/PromptSense-AI)
*Prompt quality analyzer and optimizer*

- Hybrid rule-based and transformer scoring of LLM prompts, with automatic rewrites of weak ones
- Written up as a team research paper

<img src="assets/badges/python.svg" alt="Python"/> <img src="assets/badges/transformers.svg" alt="Transformers"/> <img src="assets/badges/distilbert.svg" alt="DistilBERT"/>

</td>
</tr>
<tr>
<td width="50%" valign="top">

### [Prognix](https://github.com/adieladaniel/Prognix)
*Decision support for hospital biomedical teams*

- Predicts medical equipment failure so teams can plan ahead

<img src="assets/badges/decision-support.svg" alt="Decision support"/> <img src="assets/badges/failure-prediction.svg" alt="Failure prediction"/>

</td>
<td width="50%" valign="top">

### [Web Security Checker](https://github.com/adieladaniel/Web-Security-Checker)
*Web reconnaissance and OSINT platform*

- Full-stack platform for website security analysis

<img src="assets/badges/javascript.svg" alt="JavaScript"/>

</td>
</tr>
</table>

<p align="center"><sub>All repositories are on <a href="https://github.com/adieladaniel?tab=repositories">my profile</a>.</sub></p>

<br/>

## Right now

<div align="center">
<img src="assets/now-building.svg" width="100%" alt="Live card showing the repository I pushed to most recently"/>
</div>

<br/>

## Toolbox

<table>
<tr>
<td><b>Languages</b></td>
<td>
<img src="assets/badges/python.svg" alt="Python"/> <img src="assets/badges/java.svg" alt="Java"/> <img src="assets/badges/javascript.svg" alt="JavaScript"/> <img src="assets/badges/c.svg" alt="C"/> <img src="assets/badges/sql.svg" alt="SQL"/> <img src="assets/badges/mysql.svg" alt="MySQL"/> <img src="assets/badges/postgresql.svg" alt="PostgreSQL"/>
</td>
</tr>
<tr>
<td><b>Web and backend</b></td>
<td>
<img src="assets/badges/react.svg" alt="React"/> <img src="assets/badges/node-js.svg" alt="Node.js"/> <img src="assets/badges/express-js.svg" alt="Express.js"/> <img src="assets/badges/fastapi.svg" alt="FastAPI"/>
</td>
</tr>
<tr>
<td><b>ML and data</b></td>
<td>
<img src="assets/badges/numpy.svg" alt="NumPy"/> <img src="assets/badges/pandas.svg" alt="Pandas"/> <img src="assets/badges/scikit-learn.svg" alt="Scikit-learn"/> <img src="assets/badges/tensorflow.svg" alt="TensorFlow"/> <img src="assets/badges/pytorch.svg" alt="PyTorch"/> <img src="assets/badges/deep-learning.svg" alt="Deep learning"/> <img src="assets/badges/nlp.svg" alt="NLP"/>
</td>
</tr>
<tr>
<td><b>GenAI and agents</b></td>
<td>
<img src="assets/badges/langgraph.svg" alt="LangGraph"/> <img src="assets/badges/langchain.svg" alt="LangChain"/> <img src="assets/badges/rag.svg" alt="RAG"/> <img src="assets/badges/chromadb.svg" alt="ChromaDB"/> <img src="assets/badges/qdrant.svg" alt="Qdrant"/> <img src="assets/badges/llms.svg" alt="LLMs"/> <img src="assets/badges/hugging-face.svg" alt="Hugging Face"/>
</td>
</tr>
<tr>
<td><b>Tools</b></td>
<td>
<img src="assets/badges/git.svg" alt="Git"/> <img src="assets/badges/docker.svg" alt="Docker"/> <img src="assets/badges/power-bi.svg" alt="Power BI"/> <img src="assets/badges/tableau.svg" alt="Tableau"/> <img src="assets/badges/claude-code.svg" alt="Claude Code"/>
</td>
</tr>
</table>

<br/>

<details>
<summary><b>Certifications</b> (7)</summary>

<br/>

- Claude Code in Action, Anthropic
- AI Skills Passport, EY and Microsoft
- AWS Academy Cloud Foundations
- Prompt Engineering, Infosys Springboard
- Generative AI: From Prompts to Partnership, LinkedIn Learning
- Networking Essentials, Cisco Networking Academy
- Fundamentals of Operating System, Scaler

</details>

<br/>

<div align="center">

<sub>Thanks for stopping by. Always up for a conversation about agentic AI, GenAI or a good LeetCode problem.</sub>

<br/>

<sub>Reach me at <a href="mailto:adieladaniel2006@gmail.com">adieladaniel2006@gmail.com</a></sub>

</div>
