from fastapi import FastAPI
from fastapi.responses import JSONResponse, FileResponse
from fastapi.requests import Request
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

import sqlite3
import uuid
import time




class Project:
    id: str
    name: str
    description: str
    password: str

    def __init__(self, id: str, name: str, description: str, password: str):
        self.id = id
        self.name = name
        self.description = description
        self.password = password
    
    @staticmethod
    def from_json(data: dict):
        if "id" not in data:
            data["id"] = str(uuid.uuid4())
        return Project(data["id"], data["name"], data["description"], data["password"])

    def is_valid_password(self, password: str):
        return self.password == password
    
    def to_json(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description
        }


class Source:
    id: str
    tag: str
    url: str
    author: str
    title: str
    date_accessed: str
    date_published: str

    def __init__(self, id: str, tag: str, url: str, author: str, title: str, date_accessed: str, date_published: str):
        self.id = id
        self.tag = tag
        self.url = url
        self.author = author
        self.title = title
        self.date_accessed = date_accessed
        self.date_published = date_published
    
    @staticmethod
    def from_json(data: dict):
        return Source(data["id"], data["tag"], data["url"], data["author"], data["title"], data["date_accessed"], data["date_published"])
    
    def to_json(self):
        return {
            "id": self.id,
            "tag": self.tag,
            "url": self.url,
            "author": self.author,
            "title": self.title,
            "date_accessed": self.date_accessed,
            "date_published": self.date_published
        }
    

class DB:
    db_path: str

    conn: sqlite3.Connection
    cursor: sqlite3.Cursor

    is_locked: bool = False

    # tables:

    # Projects
    #   id
    #   name
    #   description
    #   password

    # one table for each project
    # contains sources for the project
    # <project_id>
    #   id
    #   tag
    #   url
    #   author
    #   title
    #   date_accessed
    #   date_published

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()

        self._init_tables()

    def _execute(self, cmd: str, args: tuple = (), many: bool = False):
        while self.is_locked:
            time.sleep(0.025)
        
        self.is_locked = True
        self.cursor.execute(cmd, args)

        if many:
            data = self.cursor.fetchall()
        else:
            data = self.cursor.fetchone()

        self.conn.commit()
        self.is_locked = False

        return data


    def _init_tables(self):
        cmd = """
        CREATE TABLE IF NOT EXISTS Projects (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            password TEXT NOT NULL
        );
        """
        self._execute(cmd)

    def _create_project_table(self, project_id: str):
        cmd = f"""
        CREATE TABLE IF NOT EXISTS '{project_id}' (
            id TEXT PRIMARY KEY,
            tag TEXT NOT NULL,
            url TEXT NOT NULL,
            author TEXT NOT NULL,
            title TEXT NOT NULL,
            date_accessed TEXT NOT NULL,
            date_published TEXT NOT NULL
        );
        """
        self._execute(cmd)
    
    def create_project(self, project: Project):
        self._create_project_table(project.id)
        cmd = """
        INSERT INTO Projects (id, name, description, password) VALUES (?, ?, ?, ?);
        """
        self._execute(cmd, (project.id, project.name, project.description, project.password))
    
    def read_project(self, project_id: str) -> Project:
        cmd = """
        SELECT * FROM Projects WHERE id = ?;
        """
        data = self._execute(cmd, (project_id,))
        return Project(data[0], data[1], data[2], data[3])
    
    def read_projects(self) -> list[Project]:
        cmd = """
        SELECT * FROM Projects;
        """
        data = self._execute(cmd, many=True)
        return [Project(d[0], d[1], d[2], d[3]) for d in data]
    
    def update_project(self, project: Project):
        cmd = """
        UPDATE Projects SET name = ?, description = ?, password = ? WHERE id = ?;
        """
        self._execute(cmd, (project.name, project.description, project.password, project.id))
    
    def delete_project(self, project_id: str):
        cmd = """
        DELETE FROM Projects WHERE id = ?;
        """
        self._execute(cmd, (project_id,))
        cmd = f"""
        DROP TABLE IF EXISTS '{project_id}';
        """
        self._execute(cmd)
    


    def create_source(self, project_id: str, source: Source):
        cmd = f"""
        INSERT INTO '{project_id}' (id, tag, url, author, title, date_accessed, date_published) VALUES (?, ?, ?, ?, ?, ?, ?);
        """
        self._execute(cmd, (source.id, source.tag, source.url, source.author, source.title, source.date_accessed, source.date_published))
    
    def read_source(self, project_id: str, source_id: str) -> Source:
        cmd = f"""
        SELECT * FROM '{project_id}' WHERE id = ?;
        """
        data = self._execute(cmd, (source_id,))
        return Source(data[0], data[1], data[2], data[3], data[4], data[5], data[6])
    
    def read_sources(self, project_id: str) -> list[Source]:
        cmd = f"""
        SELECT * FROM '{project_id}';
        """
        data = self._execute(cmd, many=True)
        return [Source(d[0], d[1], d[2], d[3], d[4], d[5], d[6]) for d in data]
    
    def update_source(self, project_id: str, source: Source):
        cmd = f"""
        UPDATE '{project_id}' SET tag = ?, url = ?, author = ?, title = ?, date_accessed = ?, date_published = ? WHERE id = ?;
        """
        self._execute(cmd, (source.tag, source.url, source.author, source.title, source.date_accessed, source.date_published, source.id))
    
    def delete_source(self, project_id: str, source_id: str):
        cmd = f"""
        DELETE FROM '{project_id}' WHERE id = ?;
        """
        self._execute(cmd, (source_id,))


db = DB("data.db")

# FastAPI app with CORS middleware
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



# projects
@app.get("/projects")
def get_projects(project_id: str | None = None):
    if project_id:
        project = db.read_project(project_id)
        return JSONResponse(content=project.to_json())
    projects = db.read_projects()
    return JSONResponse(content=[p.to_json() for p in projects])

@app.get("/projects/exists")
def project_exists(project_id: str):
    try:
        project = db.read_project(project_id)
        return JSONResponse(content={"exists": True})
    except:
        return JSONResponse(content={"exists": False})

@app.post("/projects")
async def create_project(request: Request):
    data = await request.json()
    project = Project.from_json(data)
    db.create_project(project)
    return JSONResponse(content=project.to_json())

@app.put("/projects")
async def update_project(request: Request):
    data = await request.json()

    old_project = db.read_project(data["id"])
    if not old_project.is_valid_password(data["old_password"]):
        return JSONResponse(content={"message": "Invalid password"}, status_code=401)

    project = Project.from_json(data)
    db.update_project(project)
    return JSONResponse(content=project.to_json())

@app.delete("/projects")
def delete_project(project_id: str, password: str):
    project = db.read_project(project_id)
    if not project.is_valid_password(password):
        return JSONResponse(content={"message": "Invalid password"}, status_code=401)
    
    db.delete_project(project_id)
    return JSONResponse(content={"message": "Project deleted"})



# sources
@app.get("/projects/{project_id}/sources")
def get_sources(project_id: str):
    sources = db.read_sources(project_id)
    return JSONResponse(content=[s.to_json() for s in sources])

@app.post("/projects/{project_id}/sources")
async def create_source(project_id: str, request: Request):
    data = await request.json()
    source = Source.from_json(data)
    db.create_source(project_id, source)
    return JSONResponse(content=source.to_json())

@app.get("/projects/{project_id}/sources/{source_id}")
def get_source(project_id: str, source_id: str):
    source = db.read_source(project_id, source_id)
    return JSONResponse(content=source.to_json())

@app.put("/projects/{project_id}/sources")
async def update_source(project_id: str, request: Request):
    data = await request.json()
    source = Source.from_json(data)
    db.update_source(project_id, source)
    return JSONResponse(content=source.to_json())

@app.delete("/projects/{project_id}/sources/{source_id}")
def delete_source(project_id: str, source_id: str):
    db.delete_source(project_id, source_id)
    return JSONResponse(content={"message": "Source deleted"})


# frontend
@app.get("/{path:path}")
def get_frontend(path: str):
    if path == "":
        path = "index.html"

    return FileResponse("../frontend/build/" + path)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=1960)