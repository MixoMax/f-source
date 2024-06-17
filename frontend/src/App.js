import {useState, useEffect} from 'react';
import SourceEditor from './components/sourceeditor';
import SourceViewer from './components/sourceviewer';
import './App.css';

function App() {
  const api_url = "http://localhost:1960"

  const [projectID, setProjectID] = useState(document.location.pathname.split("/")[1]);
  const [view_mode, setViewMode] = useState(document.location.pathname.split("/")[2]);


  return (
    <div className="App">
      {
        view_mode === "edit" ?
        <SourceEditor projectID={projectID} setProjectID={setProjectID} api_url={api_url} />
        :
        <SourceViewer projectID={projectID} api_url={api_url} />
      }
    </div>
  );
}

export default App;
