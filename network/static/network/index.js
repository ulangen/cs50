function CSRFToken() {
    const csrftoken = getCookie('csrftoken');
    return <input type="hidden" name="csrfmiddlewaretoken" value={csrftoken} />;
}

function PostCreation({ onCreate }) {
    const textareaRef = React.useRef(null);

    function handleSubmit(event) {
        event.preventDefault();
        const form = event.target;
        const formData = new FormData(form);

        fetch('/posts', {
            method: form.method,
            headers: {
                'X-CSRFToken': formData.get('csrfmiddlewaretoken'),
            },
            body: JSON.stringify({
                body: formData.get('body'),
            }),
        })
            .then((response) => response.json())
            .then((result) => {
                // Print result
                console.log(result);

                form.reset();
                textareaRef.current.focus();
                onCreate();
            });
    }

    return (
        <div className="card mb-3">
            <div className="card-body">
                <h5 className="card-title">Create a new post</h5>
                <hr />
                <form onSubmit={handleSubmit} method="post">
                    <CSRFToken />
                    <div className="form-group">
                        <textarea
                            ref={textareaRef}
                            className="form-control textarea-no-resize"
                            name="body"
                            rows={5}
                            placeholder="What's happening?"
                            autoFocus={true}
                        />
                    </div>
                    <button
                        type="submit"
                        className="btn btn-outline-primary btn-block"
                    >
                        Post
                    </button>
                </form>
            </div>
        </div>
    );
}

function Post({ postData }) {
    return (
        <div className="card mb-3">
            <div className="card-body">
                <h5 className="card-title">{postData.author}</h5>
                <p className="card-text">{postData.body}</p>
                <p className="card-text">
                    <small className="text-muted">{postData.timestamp}</small>
                </p>
                <hr />
                <ul className="card-text list-inline">
                    <li className="list-inline-item">
                        <strong>0</strong>{' '}
                        <span className="text-muted">Likes</span>
                    </li>
                </ul>
            </div>
        </div>
    );
}

function PostList({ posts }) {
    return (
        <React.Fragment>
            {posts.length ? (
                posts.map((postData) => (
                    <Post key={postData.id} postData={postData} />
                ))
            ) : (
                <div className="card">
                    <div className="card-body">
                        <p className="card-text">No posts</p>
                    </div>
                </div>
            )}
        </React.Fragment>
    );
}

function App({ isUserAuthenticated }) {
    const [posts, setPosts] = React.useState([]);

    React.useEffect(() => {
        updatePosts();
    }, []);

    function updatePosts() {
        fetch('/posts')
            .then((response) => response.json())
            .then((posts) => {
                // Print posts
                console.log(posts);
                setPosts(posts);
            });
    }

    return (
        <React.Fragment>
            {isUserAuthenticated ? (
                <PostCreation
                    onCreate={() => {
                        updatePosts();
                    }}
                />
            ) : null}
            <PostList posts={posts} />
        </React.Fragment>
    );
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === name + '=') {
                cookieValue = decodeURIComponent(
                    cookie.substring(name.length + 1)
                );
                break;
            }
        }
    }
    return cookieValue;
}

const app = document.querySelector('#app');
const isUserAuthenticated =
    app.dataset.isUserAuthenticated === 'True' ? true : false;

ReactDOM.render(<App isUserAuthenticated={isUserAuthenticated} />, app);
