# LangChain for LLM Application Development

This repository serves as a practical guide and hands-on reference for the **LangChain: Models, Prompts, and Parsers** course by DeepLearning.AI. It includes Jupyter notebooks and homework solutions that demonstrate key concepts like:

  * **Language model integration**
  * **Prompt engineering**
  * **Output parsing**

\<br\>

-----

\<br\>

## 🚀 Streamlit Chatbot Project

This project is a multi-file **Streamlit chatbot** that uses **Llama 3** via **Ollama** and **LangChain**. It's structured with dedicated modules for managing various components.

### **Getting Started**

1.  Copy all files into a single folder.
2.  Create a `core/` subdirectory and move the helper modules into it.
3.  Install the required dependencies from `requirements.txt`.
4.  Run the application using `streamlit run app.py`.

### **Project Structure**

```
.
├── app.py
├── settings.py
├── requirements.txt
└── core/
    ├── __init__.py
    ├── llm.py         # Language model setup
    ├── history.py     # Chat history management
    ├── memory.py      # Conversation memory
    ├── logs.py        # Logging functionality
    └── utils.py       # General utility functions
```