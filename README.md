# Legal Document Analysis Platform

## Overview

A comprehensive legal document analysis platform powered by Google Gemini AI that enables users to upload, process, and analyze legal documents. The application provides intelligent document parsing, AI-driven legal analysis, and analytics dashboards for document management. Built with Streamlit for an intuitive web interface, it supports multiple document formats (PDF, DOCX, TXT) and stores analysis results for historical tracking and insights.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Streamlit Web Framework**: Single-page application with sidebar navigation providing three main sections: Document Upload & Analysis, Document History, and Analytics Dashboard
- **Multi-page Navigation**: Organized into distinct functional areas using Streamlit's selectbox navigation
- **Interactive Visualizations**: Plotly-based charts and graphs for data visualization and analytics
- **Responsive Layout**: Wide layout configuration with expandable sidebar for optimal user experience

### Backend Architecture
- **Modular Component Design**: Separated concerns across specialized classes:
  - `DocumentProcessor`: Handles text extraction from multiple file formats
  - `GeminiAnalyzer`: Manages AI-powered legal document analysis
  - `Database`: Handles data persistence and retrieval
  - `Visualizations`: Creates analytics charts and dashboards
- **Text Processing Pipeline**: Multi-format document parsing supporting PDF (PyPDF2), DOCX (python-docx), and plain text files
- **AI Analysis Engine**: Google Gemini AI integration for intelligent legal document analysis with customizable analysis types and complexity levels
- **Caching Strategy**: Streamlit resource caching for component initialization to improve performance

### Data Storage
- **SQLite Database**: Local file-based database (`legal_documents.db`) for storing document metadata, content, and analysis results
- **Document Schema**: Structured storage including filename, file type, upload date, content, and JSON-serialized analysis results
- **Analysis Persistence**: Complete analysis results stored as JSON for historical tracking and comparison

### Security and Configuration
- **Environment-based Configuration**: API keys managed through environment variables
- **Error Handling**: Comprehensive exception handling across all components with user-friendly error messages
- **Input Validation**: File type validation and content extraction error handling

## External Dependencies

### AI Services
- **Google Gemini AI**: Primary AI service for legal document analysis using the `gemini-2.5-flash` model
- **Google GenAI SDK**: Official Google client library for Gemini API integration

### Document Processing Libraries
- **PyPDF2**: PDF text extraction and processing
- **python-docx**: Microsoft Word document processing
- **Streamlit**: Web application framework and UI components

### Data Visualization
- **Plotly Express & Graph Objects**: Interactive chart creation for analytics dashboard
- **Pandas**: Data manipulation and analysis for visualization preparation

### Database
- **SQLite3**: Built-in Python database engine for local data persistence
- **JSON**: Analysis result serialization and deserialization

### Development Dependencies
- **Logging**: Built-in Python logging for error tracking and debugging
- **IO Libraries**: File handling and stream processing for document uploads
- **DateTime**: Timestamp management for document tracking and analytics




A comprehensive legal document analysis platform powered by Google Gemini AI that processes and simplifies complex legal documents for users. The application features document upload capabilities, AI-powered analysis with real-time insights, visualization charts, and complete document history management with offline SQLite database storage.

## Features

- **Document Upload**: Upload PDF, DOCX, and TXT files
- **AI Analysis**: Powered by Google Gemini AI with multiple analysis types
- **Document History**: View, search, and manage analyzed documents
- **Analytics Dashboard**: Interactive charts and visualizations
- **Offline Storage**: Local SQLite database for complete offline functionality

## System Requirements

- macOS (tested on macOS 10.15+)
- Python 3.8 or higher
- Internet connection (only for AI analysis)

## Installation & Setup Instructions for Mac

### Step 1: Install Python (if not already installed)

1. Download Python from https://www.python.org/downloads/
2. Install Python 3.8 or higher
3. Verify installation by opening Terminal and running:
   ```bash
   python3 --version
   ```

### Step 2: Extract and Setup the Project

1. Extract the downloaded zip file to your desired location
2. Open Terminal and navigate to the project folder:
   ```bash
   cd /path/to/Legal-Document-Platform
   ```

### Step 3: Install Dependencies (Choose ONE method)

**Method A: Direct System Installation (Easiest)**
```bash
# Install all dependencies directly to your system
pip3 install streamlit google-genai PyPDF2 python-docx plotly pandas numpy

# Alternative: Install from requirements file
pip3 install -r setup_requirements.txt
```

**Method B: User-level Installation (If permission issues)**
```bash
# Install to user directory (no admin rights needed)
pip3 install --user streamlit google-genai PyPDF2 python-docx plotly pandas numpy

# Alternative: Install from requirements file
pip3 install --user -r setup_requirements.txt
```

**Method C: Using Homebrew (Mac users)**
```bash
# Install Python packages via Homebrew
brew install python
pip3 install streamlit google-genai PyPDF2 python-docx plotly pandas numpy
```

### Step 4: Get Google Gemini API Key

1. Go to https://ai.google.dev/
2. Click "Get API key"
3. Sign in with your Google account
4. Create a new project or select existing
5. Generate an API key
6. Copy the API key (starts with "AIza...")

### Step 5: Set Environment Variable

**Option A: Set for current session only**
```bash
export GEMINI_API_KEY="your_api_key_here"
```

**Option B: Set permanently (recommended)**
Add this line to your ~/.bash_profile or ~/.zshrc file:
```bash
echo 'export GEMINI_API_KEY="your_api_key_here"' >> ~/.zshrc
source ~/.zshrc
```

### Step 6: Run the Application

```bash
streamlit run app.py --server.port 5000
```

The application will start and automatically open in your web browser at http://localhost:5000

## Usage Guide

### 1. Document Upload
- Go to "Document Upload" section
- Choose PDF, DOCX, or TXT files
- Upload documents for processing

### 2. Document Analysis
- Go to "Document Analysis" section
- Choose analysis mode:
  - **New Analysis**: Only unanalyzed documents
  - **Re-analyze**: All documents (including previously analyzed)
- Select document and analysis options
- Click "Analyze Document"

### 3. Document History
- View all uploaded documents
- Search and filter documents
- View analysis results
- Delete unwanted documents
- See recent activity with detailed status

### 4. Analytics Dashboard
- View upload timeline charts
- See file type distribution
- Analyze document complexity
- Track document metrics

## Analysis Features

### Analysis Types
- Comprehensive Analysis
- Summary Only
- Key Points Extraction
- Risk Assessment
- Legal Entity Extraction
- Contract Review
- Compliance Check

### Detail Levels
- Basic
- Intermediate
- Advanced
- Expert

### Advanced Options
- Extract Legal Entities
- Risk Assessment
- Timeline Analysis

## Troubleshooting

### Common Issues

**1. "Module not found" error**
```bash
pip install --upgrade -r setup_requirements.txt
```

**2. "GEMINI_API_KEY not found" error**
- Verify API key is set correctly
- Restart terminal after setting environment variable

**3. Port already in use**
```bash
streamlit run app.py --server.port 8501
```

**4. Permission errors on Mac**
```bash
# If you get permission errors, try user-level installation:
pip3 install --user -r setup_requirements.txt
```

**5. Numpy error with Plotly**
```bash
# Install numpy specifically:
pip3 install numpy
# Then reinstall plotly:
pip3 install plotly
```

### Stopping the Application

Press `Ctrl+C` in the terminal to stop the application.

## Data Storage

- All data is stored locally in `legal_documents.db` (SQLite database)
- No data is sent to external servers except for AI analysis
- Documents and analysis results are saved offline

## Security Notes

- API key should be kept secure and not shared
- Documents are processed locally and only text is sent to Gemini AI
- All analysis results are stored locally

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Verify all dependencies are installed correctly
3. Ensure Python 3.8+ is being used
4. Check that the API key is set correctly

---

**Note**: This application requires an internet connection only for AI analysis. Document upload, storage, and viewing work completely offline.