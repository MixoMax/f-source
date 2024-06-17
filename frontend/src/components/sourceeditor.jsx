import {useState, useEffect} from 'react';
import SourceEntry from './sourceentry';

function SourceEditor(props) {

    const api_url = props.api_url;

    //API:
    /*
    GET /projects/exists ? project_id -> {exists: true/false}
    GET /projects ? project_id -> {id, name, description}
    POST /projects -> {name, description, password} -> same as GET
    PUT /projects -> {id, name, description, password} -> same as GET
    DELETE /projects -> {id, password} -> {success}

    GET /projects/:project_id/sources -> [{id, tag, url, author, title, date_accessed, date_published}]
    POST /projects/:project_id/sources -> {tag, url, author, title, date_accessed, date_published} -> same as GET
    PUT /projects/:project_id/sources -> {id, tag, url, author, title, date_accessed, date_published} -> same as GET
    DELETE /projects/:project_id/sources -> {id} -> {success}
    */

    const [project, setProject] = useState({});
    const [projectExists, setProjectExists] = useState(false);
    const [sources, setSources] = useState([]);
    const [sourceEntries, setSourceEntries] = useState([]);

    const [input_project_name, setInputProjectName] = useState("");
    const [input_project_description, setInputProjectDescription] = useState("");
    const [input_project_password, setInputProjectPassword] = useState("");
    const [input_create_new_project, setInputCreateNewProject] = useState(false);

    useEffect(() => {
        fetch(api_url + "/projects/exists?project_id=" + props.projectID)
        .then(response => response.json())
        .then(data => {
            setProjectExists(data.exists);
        });
    }, [props.projectID]);

    useEffect(() => {
        if (projectExists) {
            fetch(api_url + "/projects?project_id=" + props.projectID)
            .then(response => response.json())
            .then(data => {
                setProject(data);
            });
        }
    }, [props.projectID, projectExists]);

    useEffect(() => {
        if (projectExists) {
            fetch(api_url + "/projects/" + props.projectID + "/sources")
            .then(response => response.json())
            .then(data => {
                setSources(data);
            });
        }
    }, [props.projectID, projectExists]);

    useEffect(() => {
        setSourceEntries(
            sources.map(source => {
                return <SourceEntry key={source.id} source={source} />
            })
        );
    }, [sources]);

    function handleCreateOrUpdateProject() {
        var method = input_create_new_project ? "POST" : "PUT";

        if (method === "POST") {
            var payload = {
                name: input_project_name,
                description: input_project_description,
                password: input_project_password
            }
        } else {
            var payload = {
                id: props.projectID,
                name: input_project_name,
                description: input_project_description,
                password: input_project_password
            }
        }

        fetch(api_url + "/projects", {
            method: method,
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(payload)
        }).then(response => response.json())
        .then(data => {
            setProject(data);
        });
            
    }





    return (
        <div>
            <div className="project-info">
                <h1>Project Info</h1>
                <input type="text" placeholder="Project Name" value={input_project_name} onChange={e => setInputProjectName(e.target.value)} />
                <textarea placeholder="Project Description" value={input_project_description} onChange={e => setInputProjectDescription(e.target.value)}></textarea>
                <input type="password" placeholder="Project Password" value={input_project_password} onChange={e => setInputProjectPassword(e.target.value)} />
                
                <label htmlFor="create-new-project">Create New Project</label>
                <input type="checkbox" id="create-new-project" checked={input_create_new_project} onChange={e => setInputCreateNewProject(e.target.checked)} />

                <button onClick={handleCreateOrUpdateProject}>Save</button>

                <p>Project ID: {props.projectID}</p>
                <p>Project Name: {project.name}</p>
                <p>Project Description: {project.description}</p>
            </div>
            {sourceEntries}
        </div>
    );
}

export default SourceEditor;