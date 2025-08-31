import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime, timedelta
from collections import Counter
import json

def create_visualizations(documents):
    """Create various visualizations for the document analytics dashboard."""
    
    # Prepare data
    df_data = []
    for doc in documents:
        doc_id, filename, file_type, upload_date, content, analysis = doc
        
        # Parse analysis if available
        analysis_data = {}
        if analysis:
            try:
                analysis_data = json.loads(analysis)
            except json.JSONDecodeError:
                pass
        
        df_data.append({
            'id': doc_id,
            'filename': filename,
            'file_type': file_type,
            'upload_date': upload_date,
            'content_length': len(content),
            'word_count': len(content.split()),
            'complexity_score': analysis_data.get('insights', {}).get('complexity_score', 5)
        })
    
    df = pd.DataFrame(df_data)
    
    # Convert upload_date to datetime
    df['upload_date'] = pd.to_datetime(df['upload_date'])
    df['upload_day'] = df['upload_date'].dt.date
    
    # Create timeline chart
    fig_timeline = create_upload_timeline(df)
    
    # Create file types distribution
    fig_types = create_file_types_chart(df)
    
    # Create complexity distribution
    fig_complexity = create_complexity_chart(df)
    
    return fig_timeline, fig_types, fig_complexity

def create_upload_timeline(df):
    """Create a timeline chart showing document uploads over time."""
    
    # Group by day and count uploads
    daily_uploads = df.groupby('upload_day').size().reset_index(name='count')
    daily_uploads['upload_day'] = pd.to_datetime(daily_uploads['upload_day'])
    
    # Create line chart
    fig = px.line(
        daily_uploads, 
        x='upload_day', 
        y='count',
        title='Document Uploads Over Time',
        labels={'upload_day': 'Date', 'count': 'Number of Documents'},
        markers=True
    )
    
    fig.update_layout(
        height=400,
        showlegend=False,
        xaxis_title="Date",
        yaxis_title="Number of Documents"
    )
    
    fig.update_traces(
        line_color='#1f77b4',
        marker_color='#1f77b4',
        marker_size=8
    )
    
    return fig

def create_file_types_chart(df):
    """Create a pie chart showing file type distribution."""
    
    # Count file types
    file_type_counts = df['file_type'].value_counts()
    
    # Map MIME types to readable names
    type_mapping = {
        'application/pdf': 'PDF',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'DOCX',
        'application/msword': 'DOC',
        'text/plain': 'TXT'
    }
    
    # Apply mapping
    file_type_counts.index = [type_mapping.get(ft, ft) for ft in file_type_counts.index]
    
    fig = px.pie(
        values=file_type_counts.values,
        names=file_type_counts.index,
        title='File Types Distribution',
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    
    fig.update_layout(height=400)
    
    return fig

def create_complexity_chart(df):
    """Create a histogram showing document complexity distribution."""
    
    fig = px.histogram(
        df,
        x='complexity_score',
        title='Document Complexity Distribution',
        labels={'complexity_score': 'Complexity Score (1-10)', 'count': 'Number of Documents'},
        nbins=10,
        color_discrete_sequence=['#ff7f0e']
    )
    
    fig.update_layout(
        height=400,
        xaxis_title="Complexity Score (1-10)",
        yaxis_title="Number of Documents",
        showlegend=False
    )
    
    # Add average line
    avg_complexity = df['complexity_score'].mean()
    fig.add_vline(
        x=avg_complexity, 
        line_dash="dash", 
        line_color="red",
        annotation_text=f"Average: {avg_complexity:.1f}"
    )
    
    return fig

def create_document_metrics_chart(documents):
    """Create a comprehensive metrics dashboard."""
    
    # Prepare data
    df_data = []
    for doc in documents:
        doc_id, filename, file_type, upload_date, content, analysis = doc
        
        analysis_data = {}
        if analysis:
            try:
                analysis_data = json.loads(analysis)
            except json.JSONDecodeError:
                pass
        
        df_data.append({
            'filename': filename[:20] + '...' if len(filename) > 20 else filename,
            'word_count': len(content.split()),
            'complexity': analysis_data.get('insights', {}).get('complexity_score', 5),
            'upload_date': upload_date
        })
    
    df = pd.DataFrame(df_data)
    
    # Create subplots
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Word Count by Document', 'Complexity vs Word Count', 
                       'Recent Activity', 'Document Size Distribution'),
        specs=[[{"type": "bar"}, {"type": "scatter"}],
               [{"type": "bar"}, {"type": "histogram"}]]
    )
    
    # Word count bar chart
    fig.add_trace(
        go.Bar(x=df['filename'], y=df['word_count'], name='Word Count'),
        row=1, col=1
    )
    
    # Complexity vs Word Count scatter
    fig.add_trace(
        go.Scatter(x=df['word_count'], y=df['complexity'], 
                  mode='markers', name='Complexity vs Words',
                  marker=dict(size=10, opacity=0.7)),
        row=1, col=2
    )
    
    # Recent activity (last 7 documents)
    recent_df = df.tail(7)
    fig.add_trace(
        go.Bar(x=recent_df['filename'], y=recent_df['word_count'], 
               name='Recent Docs'),
        row=2, col=1
    )
    
    # Document size distribution
    fig.add_trace(
        go.Histogram(x=df['word_count'], name='Size Distribution', nbinsx=10),
        row=2, col=2
    )
    
    fig.update_layout(height=800, showlegend=False, title_text="Document Analytics Dashboard")
    
    return fig

def create_advanced_analytics(documents):
    """Create advanced analytics charts for legal document insights."""
    
    # Extract analysis data
    complexity_scores = []
    legal_areas = []
    sentiment_scores = []
    
    for doc in documents:
        _, _, _, _, _, analysis = doc
        
        if analysis:
            try:
                analysis_data = json.loads(analysis)
                insights = analysis_data.get('insights', {})
                
                # Complexity scores
                if 'complexity_score' in insights:
                    complexity_scores.append(insights['complexity_score'])
                
                # Legal areas
                if 'legal_areas' in insights:
                    legal_areas.extend(insights['legal_areas'])
                
                # Sentiment (if available)
                if 'sentiment' in insights:
                    sentiment_scores.append(insights['sentiment'])
                    
            except json.JSONDecodeError:
                continue
    
    # Create legal areas frequency chart
    if legal_areas:
        area_counts = Counter(legal_areas)
        
        fig_areas = px.bar(
            x=list(area_counts.values()),
            y=list(area_counts.keys()),
            orientation='h',
            title='Most Common Legal Areas',
            labels={'x': 'Frequency', 'y': 'Legal Areas'}
        )
        
        fig_areas.update_layout(height=400)
    else:
        fig_areas = go.Figure()
        fig_areas.add_annotation(text="No legal area data available", 
                               xref="paper", yref="paper",
                               x=0.5, y=0.5, showarrow=False)
    
    return fig_areas

def create_trend_analysis(documents):
    """Create trend analysis showing document patterns over time."""
    
    # Prepare monthly data
    df_data = []
    for doc in documents:
        doc_id, filename, file_type, upload_date, content, analysis = doc
        
        upload_dt = datetime.strptime(upload_date, "%Y-%m-%d %H:%M:%S")
        month_year = upload_dt.strftime("%Y-%m")
        
        df_data.append({
            'month': month_year,
            'word_count': len(content.split()),
            'file_type': file_type
        })
    
    df = pd.DataFrame(df_data)
    
    # Monthly document count and average length
    monthly_stats = df.groupby('month').agg({
        'word_count': ['count', 'mean']
    }).round(0)
    
    monthly_stats.columns = ['doc_count', 'avg_length']
    monthly_stats = monthly_stats.reset_index()
    
    # Create dual y-axis chart
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Document count
    fig.add_trace(
        go.Scatter(x=monthly_stats['month'], y=monthly_stats['doc_count'],
                  mode='lines+markers', name='Document Count',
                  line=dict(color='blue')),
        secondary_y=False,
    )
    
    # Average length
    fig.add_trace(
        go.Scatter(x=monthly_stats['month'], y=monthly_stats['avg_length'],
                  mode='lines+markers', name='Avg Word Count',
                  line=dict(color='red')),
        secondary_y=True,
    )
    
    # Update axes labels
    fig.update_xaxes(title_text="Month")
    fig.update_yaxes(title_text="Number of Documents", secondary_y=False)
    fig.update_yaxes(title_text="Average Word Count", secondary_y=True)
    
    fig.update_layout(title_text="Document Upload Trends", height=400)
    
    return fig
