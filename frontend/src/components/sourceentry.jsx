import {useState, useEffect} from 'react';

function SourceEntry(props) {

    if (props.mode === "view") {
        return (
            <div className="source-entry" onClick={() => document.location.href = "/source/" + props.source.url}>
                <div className="hbox">
                    <h3>{props.source.tag}</h3>
                    <h3>{props.source.title}</h3>
                    <h3>{props.source.author}</h3>
                    <div className="date-box">
                        <h3>{props.source.date_accessed}</h3>
                        <h3>{props.source.date_published}</h3>
                    </div>
                </div>
            </div>
        );
    } else {
        return (
            <div className="source-entry">
                <div className="hbox">
                    <input type="text" value={props.source.tag} onChange={(e) => props.onChange(props.source.id, "tag", e.target.value)} />
                    <input type="text" value={props.source.title} onChange={(e) => props.onChange(props.source.id, "title", e.target.value)} />
                    <input type="text" value={props.source.author} onChange={(e) => props.onChange(props.source.id, "author", e.target.value)} />
                    <div className="date-box">
                        <input type="text" value={props.source.date_accessed} onChange={(e) => props.onChange(props.source.id, "date_accessed", e.target.value)} />
                        <input type="text" value={props.source.date_published} onChange={(e) => props.onChange(props.source.id, "date_published", e.target.value)} />
                    </div>
                </div>
            </div>
        );
    }
}

export default SourceEntry;