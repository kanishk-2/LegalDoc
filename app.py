import streamlit as st
import os
import json
import sqlite3
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from database import Database
from document_processor import DocumentProcessor
from gemini_analyzer import GeminiAnalyzer
from visualizations import create_visualizations

# Page configuration
st.set_page_config(
    page_title="Legal Document Analysis Platform",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize components
@st.cache_resource
def init_components():
    db = Database()
    processor = DocumentProcessor()
    analyzer = GeminiAnalyzer()
    return db, processor, analyzer

db, processor, analyzer = init_components()

# Main title
st.title("⚖️ Legal Document Analysis Platform")
st.markdown("*Powered by Google Gemini AI*")

# Sidebar navigation
st.sidebar.title("📁 Navigation")
page = st.sidebar.selectbox(
    "Choose a section:",
    ["Document Upload", "Document Analysis", "Document History", "Analytics Dashboard"]
)

if page == "Document Upload":
    st.header("📄 Document Upload")
    
    # File upload
    uploaded_file = st.file_uploader(
        "Choose a legal document",
        type=["pdf", "docx", "txt"],
        help="Upload PDF, DOCX, or TXT files"
    )
    
    if uploaded_file is not None:
        # Display file info
        st.success(f"File uploaded: {uploaded_file.name} ({uploaded_file.size} bytes)")
        
        # Extract and store document
        with st.spinner("Processing document..."):
            try:
                # Extract text from document
                extracted_text = processor.extract_text(uploaded_file)
                
                if not extracted_text.strip():
                    st.error("Could not extract text from the document. Please check the file format.")
                else:
                    # Store document without analysis initially
                    doc_id = db.store_document(
                        filename=uploaded_file.name,
                        content=extracted_text,
                        analysis={"status": "uploaded", "analyzed": False},
                        file_type=uploaded_file.type
                    )
                    
                    st.success(f"✅ Document uploaded and stored with ID: {doc_id}")
                    st.info("📋 Document is ready for analysis. Go to 'Document Analysis' section to analyze it.")
                    
                    # Show document preview
                    st.subheader("📖 Document Preview")
                    st.text_area("Content Preview (first 500 characters):", 
                               value=extracted_text[:500] + "..." if len(extracted_text) > 500 else extracted_text,
                               height=200, disabled=True)
                    
                    # Show document metrics
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Word Count", len(extracted_text.split()))
                    with col2:
                        st.metric("Character Count", len(extracted_text))
                    with col3:
                        st.metric("Reading Time", f"{len(extracted_text.split()) // 200 + 1} min")
                        
            except Exception as e:
                st.error(f"Error processing document: {str(e)}")

elif page == "Document Analysis":
    st.header("🔍 Document Analysis")
    
    # Get all documents
    all_documents = db.get_all_documents()
    
    if not all_documents:
        st.info("📭 No documents available for analysis. Please upload documents first.")
        st.markdown("[Go to Document Upload →]()", unsafe_allow_html=True)
    else:
        # Analysis mode selection
        st.subheader("📋 Analysis Mode")
        analysis_mode = st.radio(
            "Choose analysis type:",
            ["🆕 New Analysis (Unanalyzed Documents)", "🔄 Re-analyze Documents (All Documents)"],
            help="Select whether to analyze new documents or re-analyze existing documents"
        )
        
        # Filter documents based on mode
        if analysis_mode.startswith("🆕"):
            # Filter for documents that haven't been analyzed yet
            available_docs = []
            for doc in all_documents:
                doc_id, filename, file_type, upload_date, content, analysis = doc
                if analysis:
                    try:
                        analysis_data = json.loads(analysis)
                        # Check if document has been analyzed (default to False for new uploads)
                        if not analysis_data.get("analyzed", False):
                            available_docs.append(doc)
                    except json.JSONDecodeError:
                        # If analysis data is corrupted, consider it unanalyzed
                        available_docs.append(doc)
                else:
                    # No analysis data means it hasn't been analyzed
                    available_docs.append(doc)
            
            if not available_docs:
                st.info("📭 No unanalyzed documents available. All documents have been analyzed.")
                st.info("💡 Switch to 'Re-analyze Documents' mode to analyze existing documents again.")
            else:
                st.write(f"📊 {len(available_docs)} document(s) ready for analysis")
        else:
            # Show all documents for re-analysis
            available_docs = all_documents
            st.write(f"📊 {len(available_docs)} document(s) available for re-analysis")
        
        if available_docs:
            # Document selection
            doc_options = []
            for doc in available_docs:
                doc_id, filename, file_type, upload_date, content, analysis = doc
                
                # Get analysis status for display
                status_indicator = ""
                if analysis:
                    try:
                        analysis_data = json.loads(analysis)
                        if analysis_data.get("analyzed", False):
                            status_indicator = " ✅"
                        else:
                            status_indicator = " ⏳"
                    except json.JSONDecodeError:
                        status_indicator = " ❌"
                else:
                    status_indicator = " 📝"
                
                doc_options.append((f"{filename}{status_indicator} (ID: {doc_id}) - {upload_date[:10]}", doc_id))
            
            selected_doc_label = st.selectbox(
                "Choose a document to analyze:",
                options=[option[0] for option in doc_options],
                help="✅ = Analyzed, ⏳ = Pending, ❌ = Error, 📝 = New"
            )
            
            if selected_doc_label:
                # Find selected document
                selected_doc_id = next(option[1] for option in doc_options if option[0] == selected_doc_label)
                selected_doc = next(doc for doc in available_docs if doc[0] == selected_doc_id)
                
                doc_id, filename, file_type, upload_date, content, analysis = selected_doc
                
                # Show document info
                st.subheader(f"📄 {filename}")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("File Type", file_type.split('/')[-1].upper())
                with col2:
                    st.metric("Upload Date", upload_date[:10])
                with col3:
                    st.metric("Word Count", len(content.split()))
                
                # Analysis options
                st.subheader("⚙️ Analysis Configuration")
                col1, col2 = st.columns(2)
                
                with col1:
                    analysis_type = st.selectbox(
                        "Analysis Type:",
                        ["Comprehensive Analysis", "Summary Only", "Key Points Extraction", "Risk Assessment", "Legal Entity Extraction", "Contract Review", "Compliance Check"]
                    )
                
                with col2:
                    complexity_level = st.select_slider(
                        "Detail Level:",
                        options=["Basic", "Intermediate", "Advanced", "Expert"],
                        value="Intermediate"
                    )
                
                # Additional analysis options
                st.subheader("🔧 Advanced Options")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    include_entities = st.checkbox("Extract Legal Entities", value=True)
                with col2:
                    include_risks = st.checkbox("Risk Assessment", value=True)
                with col3:
                    include_timeline = st.checkbox("Timeline Analysis", value=False)
                
                # Analyze button
                if st.button("🔍 Analyze Document", type="primary"):
                    with st.spinner("Analyzing document with Gemini AI..."):
                        try:
                            # Perform AI analysis
                            analysis_result = analyzer.analyze_document(
                                content, 
                                analysis_type, 
                                complexity_level
                            )
                            
                            # Mark as analyzed and update in database
                            analysis_result["analyzed"] = True
                            analysis_result["analysis_date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            analysis_result["analysis_type"] = analysis_type
                            analysis_result["complexity_level"] = complexity_level
                            analysis_result["advanced_options"] = {
                                "entities": include_entities,
                                "risks": include_risks,
                                "timeline": include_timeline
                            }
                            
                            # Update the document with analysis
                            with sqlite3.connect(db.db_path) as conn:
                                cursor = conn.cursor()
                                cursor.execute(
                                    "UPDATE documents SET analysis = ? WHERE id = ?",
                                    (json.dumps(analysis_result), doc_id)
                                )
                                conn.commit()
                            
                            # Display results
                            st.subheader("📊 Analysis Results")
                            
                            # Create tabs for different sections
                            tab1, tab2, tab3, tab4 = st.tabs(["Summary", "Key Points", "Insights", "Metrics"])
                            
                            with tab1:
                                st.markdown("### 📝 Document Summary")
                                st.write(analysis_result.get("summary", "No summary available"))
                            
                            with tab2:
                                st.markdown("### 🔑 Key Points")
                                key_points = analysis_result.get("key_points", [])
                                if key_points:
                                    for i, point in enumerate(key_points, 1):
                                        st.write(f"{i}. {point}")
                                else:
                                    st.write("No key points extracted")
                            
                            with tab3:
                                st.markdown("### 💡 AI Insights")
                                insights = analysis_result.get("insights", {})
                                
                                if "complexity_score" in insights:
                                    st.metric("Complexity Score", f"{insights['complexity_score']}/10")
                                
                                if "sentiment" in insights:
                                    st.metric("Document Tone", insights["sentiment"])
                                
                                if "legal_areas" in insights:
                                    st.write("**Legal Areas Identified:**")
                                    for area in insights["legal_areas"]:
                                        st.write(f"- {area}")
                            
                            with tab4:
                                st.markdown("### 📈 Document Metrics")
                                
                                # Create metrics
                                metrics_data = {
                                    "Word Count": len(content.split()),
                                    "Character Count": len(content),
                                    "Estimated Reading Time": f"{len(content.split()) // 200 + 1} min",
                                    "Complexity Level": analysis_result.get("insights", {}).get("complexity_level", "Unknown")
                                }
                                
                                for metric, value in metrics_data.items():
                                    st.metric(metric, value)
                            
                            st.success(f"✅ Document analysis completed and saved!")
                            
                        except Exception as e:
                            st.error(f"Error during analysis: {str(e)}")
                            st.info("Please check your internet connection and API configuration.")

elif page == "Document History":
    st.header("📚 Document History")
    
    # Fetch all documents
    documents = db.get_all_documents()
    
    if not documents:
        st.info("📭 No documents found. Upload and analyze documents to see them here.")
    else:
        st.write(f"Total documents: {len(documents)}")
        
        # Search and filter
        col1, col2 = st.columns([2, 1])
        with col1:
            search_term = st.text_input("🔍 Search documents by filename:")
        with col2:
            sort_option = st.selectbox("Sort by:", ["Date (Newest)", "Date (Oldest)", "Filename"])
        
        # Filter documents
        filtered_docs = documents
        if search_term:
            filtered_docs = [doc for doc in documents if search_term.lower() in doc[1].lower()]
        
        # Sort documents
        if sort_option == "Date (Newest)":
            filtered_docs.sort(key=lambda x: x[5], reverse=True)
        elif sort_option == "Date (Oldest)":
            filtered_docs.sort(key=lambda x: x[5])
        else:
            filtered_docs.sort(key=lambda x: x[1])
        
        # Display documents
        for doc in filtered_docs:
            doc_id, filename, file_type, upload_date, content, analysis = doc
            
            with st.expander(f"📄 {filename} - {upload_date}"):
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    st.write(f"**File Type:** {file_type}")
                    st.write(f"**Upload Date:** {upload_date}")
                    st.write(f"**Content Length:** {len(content)} characters")
                
                with col2:
                    if st.button(f"👁️ View Details", key=f"view_{doc_id}"):
                        st.session_state[f"show_details_{doc_id}"] = True
                
                with col3:
                    if st.button(f"🗑️ Delete", key=f"delete_{doc_id}", type="secondary"):
                        if db.delete_document(doc_id):
                            st.success("Document deleted successfully!")
                            st.rerun()
                        else:
                            st.error("Failed to delete document")
                
                # Show details if requested
                if st.session_state.get(f"show_details_{doc_id}", False):
                    st.markdown("**Analysis Results:**")
                    
                    if analysis:
                        import json
                        try:
                            analysis_data = json.loads(analysis)
                            
                            if "summary" in analysis_data:
                                st.write("**Summary:**")
                                st.write(analysis_data["summary"])
                            
                            if "key_points" in analysis_data:
                                st.write("**Key Points:**")
                                for point in analysis_data["key_points"]:
                                    st.write(f"- {point}")
                                    
                        except json.JSONDecodeError:
                            st.write("Analysis data is not in valid format")
                    else:
                        st.write("No analysis data available")
                    
                    if st.button(f"Hide Details", key=f"hide_{doc_id}"):
                        st.session_state[f"show_details_{doc_id}"] = False
                        st.rerun()
        
        # Recent Activity Section
        st.subheader("🕒 Recent Activity")
        recent_docs = sorted(documents, key=lambda x: x[5], reverse=True)[:5]
        
        if recent_docs:
            for doc in recent_docs:
                doc_id, filename, file_type, upload_date, content, analysis = doc
                
                # Parse analysis status
                analysis_status = "Not Analyzed"
                analysis_date = "N/A"
                if analysis:
                    try:
                        analysis_data = json.loads(analysis)
                        if analysis_data.get("analyzed", False):
                            analysis_status = "✅ Analyzed"
                            analysis_date = analysis_data.get("analysis_date", "Unknown")
                        else:
                            analysis_status = "⏳ Pending Analysis"
                    except json.JSONDecodeError:
                        analysis_status = "❌ Analysis Error"
                
                with st.container():
                    col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
                    
                    with col1:
                        st.write(f"📄 **{filename}**")
                        st.caption(f"Words: {len(content.split())} | Size: {len(content)} chars")
                    
                    with col2:
                        st.write(f"**Type:** {file_type.split('/')[-1].upper()}")
                        st.caption(f"Uploaded: {upload_date[:10]}")
                    
                    with col3:
                        st.write(f"**Status:** {analysis_status}")
                        if analysis_date != "N/A":
                            st.caption(f"Analyzed: {analysis_date[:10]}")
                    
                    with col4:
                        if st.button(f"📖 View", key=f"recent_view_{doc_id}"):
                            st.session_state[f"show_details_{doc_id}"] = True
                            st.rerun()
                    
                    st.divider()
        else:
            st.info("No recent activity to display.")

elif page == "Analytics Dashboard":
    st.header("📊 Analytics Dashboard")
    
    documents = db.get_all_documents()
    
    if not documents:
        st.info("📊 No data available. Analyze some documents first to see analytics.")
    else:
        # Create visualizations
        fig_timeline, fig_types, fig_complexity = create_visualizations(documents)
        
        # Display metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Documents", len(documents))
        
        with col2:
            total_chars = sum(len(doc[4]) for doc in documents)
            st.metric("Total Characters", f"{total_chars:,}")
        
        with col3:
            avg_length = total_chars // len(documents) if documents else 0
            st.metric("Avg Document Length", f"{avg_length:,}")
        
        with col4:
            # Get most recent upload
            latest_doc = max(documents, key=lambda x: x[5])
            st.metric("Latest Upload", latest_doc[5][:10])
        
        # Display charts
        st.subheader("📈 Upload Timeline")
        st.plotly_chart(fig_timeline, use_container_width=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📁 File Types Distribution")
            st.plotly_chart(fig_types, use_container_width=True)
        
        with col2:
            st.subheader("📊 Document Complexity")
            st.plotly_chart(fig_complexity, use_container_width=True)
        

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("### ℹ️ About")
st.sidebar.markdown(
    "This platform uses Google Gemini AI to analyze legal documents and provide "
    "insights, summaries, and visualizations. All data is stored locally using SQLite."
)

