# view_database.py - Database Viewer

import streamlit as st
import pandas as pd
import sqlite3
from sqlite3 import Error

def create_connection():
    """Create a database connection"""
    try:
        conn = sqlite3.connect('depression_data.db')
        return conn
    except Error as e:
        st.error(f"Error connecting to database: {e}")
    return None

def main():
    st.set_page_config(
        page_title="Database Viewer",
        page_icon="📊",
        layout="wide"
    )
    
    st.title("📊 Database Viewer")
    
    password = st.text_input("Enter Admin Password", type="password")
    
    if password == "admin123":
        conn = create_connection()
        
        if conn:
            cursor = conn.cursor()
            
            # Get all table names
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
            tables = cursor.fetchall()
            
            if tables:
                st.sidebar.header("Navigation")
                
                # Create tabs for each table
                table_names = [table[0] for table in tables]
                tabs = st.tabs(table_names)
                
                for i, table_name in enumerate(table_names):
                    with tabs[i]:
                        st.subheader(f"Table: {table_name}")
                        
                        # Get column information
                        cursor.execute(f"PRAGMA table_info({table_name})")
                        columns = cursor.fetchall()
                        
                        # Get all data
                        cursor.execute(f"SELECT * FROM {table_name}")
                        data = cursor.fetchall()
                        
                        if data:
                            # Create dataframe
                            column_names = [col[1] for col in columns]
                            df = pd.DataFrame(data, columns=column_names)
                            
                            # Display with sorting and filtering
                            st.dataframe(
                                df,
                                use_container_width=True,
                                height=400
                            )
                            
                            # Statistics
                            col1, col2 = st.columns(2)
                            with col1:
                                st.metric("Total Rows", len(df))
                            with col2:
                                st.metric("Total Columns", len(columns))
                            
                            # Column details
                            with st.expander("Column Details"):
                                col_data = []
                                for col in columns:
                                    col_data.append({
                                        'Column Name': col[1],
                                        'Data Type': col[2],
                                        'Nullable': 'Yes' if col[3] == 0 else 'No',
                                        'Primary Key': 'Yes' if col[5] == 1 else 'No'
                                    })
                                col_df = pd.DataFrame(col_data)
                                st.dataframe(col_df, use_container_width=True)
                            
                            # Query interface
                            with st.expander("Run Custom Query"):
                                query = st.text_area(
                                    "SQL Query",
                                    value=f"SELECT * FROM {table_name} LIMIT 10",
                                    height=100
                                )
                                
                                if st.button("Execute Query", key=f"query_{i}"):
                                    try:
                                        result = pd.read_sql_query(query, conn)
                                        st.dataframe(result, use_container_width=True)
                                        st.success(f"Query executed successfully. Returned {len(result)} rows.")
                                    except Exception as e:
                                        st.error(f"Query error: {e}")
                        else:
                            st.info("No data in this table.")
                            
                        # Export options
                        if data:
                            csv = df.to_csv(index=False)
                            st.download_button(
                                label=f"📥 Download {table_name} as CSV",
                                data=csv,
                                file_name=f"{table_name}_{pd.Timestamp.now().strftime('%Y%m%d')}.csv",
                                mime="text/csv",
                                key=f"download_{i}"
                            )
            else:
                st.warning("No tables found in the database.")
            
            conn.close()
            
            # Database summary
            st.sidebar.header("Database Summary")
            conn = create_connection()
            if conn:
                cursor = conn.cursor()
                
                for table in tables:
                    table_name = table[0]
                    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                    count = cursor.fetchone()[0]
                    st.sidebar.metric(table_name, count)
                
                conn.close()
    else:
        st.warning("Please enter the correct password to access the database viewer.")

if __name__ == "__main__":
    main()