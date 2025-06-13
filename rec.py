import os
import pandas as pd
import psycopg2
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv('db.env')

def get_resume_data(file_path='resume_data.csv'):
    df = pd.read_csv(file_path)
    # Get the first row as a dict
    data = df.iloc[0].to_dict()
    # Convert skills_list from string to Python list if needed
    try:
        import ast
        data['skills_list'] = ast.literal_eval(data.get('skills_list', '[]'))
    except Exception:
        data['skills_list'] = []
    return data

def connect_to_db():
    try:
        conn = psycopg2.connect(
            dbname=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            host=os.getenv('DB_HOST'),
            port=os.getenv('DB_PORT', '5432')
        )
        return conn
    except Exception as e:
        print(f"Database connection failed: {e}")
        return None

def recommend_jobs(skills_list, conn):
    if not skills_list:
        print("No skills provided.")
        return []
    # Lowercase all skills for matching
    skills_list = [s.lower() for s in skills_list]
    with conn.cursor() as cur:
        query = """
        SELECT DISTINCT j.job_id, j.job_title
        FROM jobs j
        JOIN job_skills js ON j.job_id = js.job_id
        JOIN skills s ON js.skill_id = s.skill_id
        WHERE LOWER(s.skill_name) = ANY(%s)
        LIMIT 10;
        """
        cur.execute(query, (skills_list,))
        return cur.fetchall()

def display_recommendations(jobs):
    if not jobs:
        print("No matching jobs found.")
        return
    print("\nTop Job Recommendations:")
    for i, job in enumerate(jobs, 1):
        print(f"{i}. {job[1]} (Job ID: {job[0]})")

if __name__ == "__main__":
    resume_data = get_resume_data(r"C:\ml\jobrec\resume_data.csv")
    print("Resume Data Loaded:")
    print(f"Name: {resume_data.get('name')}")
    print(f"Skills: {resume_data.get('skills_list')}")
    conn = connect_to_db()
    if conn:
        jobs = recommend_jobs(resume_data.get('skills_list', []), conn)
        display_recommendations(jobs)
        conn.close()