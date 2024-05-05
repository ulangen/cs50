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
                            className="form-control bg-light textarea-no-resize"
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

function Post({
    userData,
    postData,
    isEdited = false,
    onClickAuthor,
    onToggleEditing = () => {},
    onUpdatePost = () => {},
}) {
    const textareaRef = React.useRef(null);

    function handleClickAuthor(event) {
        event.preventDefault();
        onClickAuthor(postData.author_id);
    }

    function handleSavePost() {
        const textarea = textareaRef.current;

        fetch(`/posts/${postData.id}`, {
            method: 'put',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
            },
            body: JSON.stringify({
                body: textarea.value,
            }),
        }).then(() => {
            onUpdatePost();
        });
    }

    function handleLike() {
        fetch(`/posts/${postData.id}`, {
            method: 'put',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
            },
            body: JSON.stringify({
                liked: !postData.is_liked,
            }),
        }).then(() => {
            onUpdatePost();
        });
    }

    let postBody = null;

    if (isEdited) {
        postBody = (
            <div className="form-group">
                <textarea
                    autoFocus={true}
                    ref={textareaRef}
                    className="form-control bg-light textarea-no-resize"
                    defaultValue={postData.body}
                    name="body"
                    rows={5}
                />
            </div>
        );
    } else {
        postBody = <p className="card-text post-body-text">{postData.body}</p>;
    }

    return (
        <div className="card mb-3">
            <div className="card-body">
                <h5 className="card-title">
                    <a
                        className="text-reset"
                        href={postData.author}
                        onClick={handleClickAuthor}
                    >
                        {postData.author}
                    </a>
                </h5>
                {postBody}
                <p className="card-text">
                    <small className="text-muted">{postData.timestamp}</small>
                </p>
                <hr />
                <ul className="card-text list-inline">
                    <li className="list-inline-item">
                        <strong>{postData.number_of_likes}</strong>{' '}
                        <span className="text-muted">Likes</span>
                    </li>
                </ul>
                {userData.isAuthenticated && (
                    <React.Fragment>
                        <hr />
                        <ul className="card-text list-inline">
                            <li className="list-inline-item">
                                <button
                                    className="btn btn-link"
                                    onClick={handleLike}
                                >
                                    {postData.is_liked ? (
                                        <React.Fragment>
                                            <i class="bi bi-heart-fill text-danger"></i>
                                        </React.Fragment>
                                    ) : (
                                        <React.Fragment>
                                            <i class="bi bi-heart"></i>
                                        </React.Fragment>
                                    )}
                                </button>
                            </li>
                            {userData.id === postData.author_id && (
                                <React.Fragment>
                                    <li className="list-inline-item">
                                        <button
                                            className="btn btn-link"
                                            onClick={() =>
                                                onToggleEditing(
                                                    postData.id,
                                                    !isEdited
                                                )
                                            }
                                        >
                                            {isEdited ? 'Cancel' : 'Edit'}
                                        </button>
                                    </li>
                                    <li className="list-inline-item">
                                        {isEdited && (
                                            <button
                                                className="btn btn-link"
                                                onClick={handleSavePost}
                                            >
                                                Save
                                            </button>
                                        )}
                                    </li>
                                </React.Fragment>
                            )}
                        </ul>
                    </React.Fragment>
                )}
            </div>
        </div>
    );
}

function PaginationButton({
    isDisabled = false,
    isActive = false,
    children = '',
    onClick = () => {},
}) {
    return (
        <li
            className={
                'page-item' +
                (isDisabled ? ' disabled' : '') +
                (isActive ? ' active' : '')
            }
        >
            <button
                disabled={isDisabled}
                className="page-link"
                onClick={() => onClick()}
            >
                {children}
            </button>
        </li>
    );
}

function PostPagination({
    hasPrefious = false,
    hasNext = false,
    currentPage = -1,
    divider = null,
    pageRange = [],
    loadPage = () => {},
}) {
    return (
        <nav>
            <ul className="pagination justify-content-center">
                <PaginationButton
                    isDisabled={!hasPrefious}
                    onClick={() => loadPage(currentPage - 1)}
                >
                    Previous
                </PaginationButton>
                {pageRange.map((value, index) => (
                    <PaginationButton
                        key={index}
                        isDisabled={value === divider ? true : false}
                        isActive={value === currentPage ? true : false}
                        onClick={() => loadPage(value)}
                    >
                        {value}
                    </PaginationButton>
                ))}
                <PaginationButton
                    isDisabled={!hasNext}
                    onClick={() => loadPage(currentPage + 1)}
                >
                    Next
                </PaginationButton>
            </ul>
        </nav>
    );
}

function PostList({ userData, config, onClickAuthor }) {
    const [posts, setPosts] = React.useState([]);
    const [paginator, setPaginator] = React.useState({});

    React.useEffect(() => loadPosts(1, 10), [config]);

    function handleLoadPage(pageNumber) {
        loadPosts(pageNumber, 10, paginator.startswith);
        window.scrollTo(0, 0);
    }

    function handleTogglePostEditing(editedPostId, isEdited) {
        setPosts(
            posts.map((post) => ({
                ...post,
                isEdited: isEdited && post.id === editedPostId ? true : false,
            }))
        );
    }

    function loadPosts(pageNumber, perPage, startswith) {
        const data = [];
        if (pageNumber) data.push(`page=${pageNumber}`);
        if (perPage) data.push(`per_page=${perPage}`);
        if (startswith) data.push(`startswith=${startswith}`);

        const url =
            config.postApiUrl + (data.length ? '?' + data.join('&') : '');

        fetch(url)
            .then((response) => response.json())
            .then((response) => {
                // Print posts
                console.log(response);
                setPosts(response.data);
                setPaginator(response.page);
            });
    }

    return (
        <React.Fragment>
            {posts.length !== 0 ? (
                <React.Fragment>
                    {posts.map((postData) => (
                        <Post
                            userData={userData}
                            isEdited={postData.isEdited}
                            key={postData.id}
                            postData={postData}
                            onClickAuthor={onClickAuthor}
                            onToggleEditing={handleTogglePostEditing}
                            onUpdatePost={() =>
                                loadPosts(
                                    paginator.current,
                                    10,
                                    paginator.startswith
                                )
                            }
                        />
                    ))}
                    <PostPagination
                        hasPrefious={paginator.has_previous}
                        hasNext={paginator.has_next}
                        currentPage={paginator.current}
                        divider={paginator.divider}
                        pageRange={paginator.page_range}
                        loadPage={handleLoadPage}
                    />
                </React.Fragment>
            ) : (
                <div className="card mb-3">
                    <div className="card-body">
                        <p className="card-text">No posts</p>
                    </div>
                </div>
            )}
        </React.Fragment>
    );
}

function AllPostsPage({ config, onClickAuthor }) {
    const [postListConfig, setPostListConfig] = React.useState({
        postApiUrl: config.page.postApiUrl,
        userId: config.user.id,
    });

    return (
        <React.Fragment>
            {config.user.isAuthenticated ? (
                <PostCreation
                    onCreate={() => setPostListConfig({ ...postListConfig })}
                />
            ) : null}
            <PostList
                userData={config.user}
                config={postListConfig}
                onClickAuthor={onClickAuthor}
            />
        </React.Fragment>
    );
}

function UserProfile({ config }) {
    const [userData, setUserData] = React.useState({});

    React.useEffect(() => updateUserProfile(), []);

    function handleChangeFollow(isFollowed) {
        fetch(`/users/${userData.id}`, {
            method: 'post',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
            },
            body: JSON.stringify({
                followed: isFollowed,
            }),
        }).then(() => updateUserProfile());
    }

    function updateUserProfile() {
        fetch(`/users/${config.page.user_id}`)
            .then((response) => response.json())
            .then((userData) => {
                // Print user
                console.log(userData);
                setUserData(userData);
            });
    }

    let followButton;

    if (config.user.isAuthenticated && !userData.is_author_is_user) {
        if (userData.is_followed) {
            followButton = (
                <button
                    className="btn btn-outline-danger rounded-pill"
                    onClick={() => handleChangeFollow(false)}
                >
                    Unfollow
                </button>
            );
        } else {
            followButton = (
                <button
                    className="btn btn-outline-primary rounded-pill"
                    onClick={() => handleChangeFollow(true)}
                >
                    Follow
                </button>
            );
        }
    }

    return (
        <div className="card mb-3">
            <div className="card-body">
                <div className="d-flex justify-content-between align-items-center">
                    <h3 class="card-title mb-0">{userData.username}</h3>
                    {followButton}
                </div>
                <hr />
                <ul className="card-text list-inline">
                    <li className="list-inline-item">
                        <strong>{userData.readers}</strong>{' '}
                        <span className="text-muted">Followers</span>
                    </li>
                    <li className="list-inline-item">
                        <strong>{userData.authors}</strong>{' '}
                        <span className="text-muted">Following</span>
                    </li>
                </ul>
            </div>
        </div>
    );
}

function UserProfilePage({ config }) {
    const postListConfig = {
        postApiUrl: config.page.postApiUrl,
    };

    return (
        <React.Fragment>
            <UserProfile config={config} />
            <PostList
                userData={config.user}
                config={postListConfig}
                onClickAuthor={() => {}}
            />
        </React.Fragment>
    );
}

function SubscriptionPostsPage({ config, onClickAuthor }) {
    const postListConfig = { ...config.page };

    return (
        <PostList
            userData={config.user}
            config={postListConfig}
            onClickAuthor={onClickAuthor}
        />
    );
}

function App({ initConfig }) {
    const [config, setConfig] = React.useState({ ...initConfig });

    function handleClickAuthor(id) {
        setConfig({
            ...config,
            page: {
                name: 'user_profile',
                postApiUrl: `/users/${id}/posts`,
                user_id: id,
            },
        });
    }

    switch (config.page.name) {
        case 'all_posts':
            return (
                <AllPostsPage
                    config={config}
                    onClickAuthor={handleClickAuthor}
                />
            );

        case 'user_profile':
            return (
                <UserProfilePage
                    config={config}
                    onClickAuthor={handleClickAuthor}
                />
            );

        case 'subscriptions':
            return (
                <SubscriptionPostsPage
                    config={config}
                    onClickAuthor={handleClickAuthor}
                />
            );

        default:
            return <p>Page not found</p>;
    }
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

const userId = app.dataset.userId;

const config = {
    user: {
        isAuthenticated:
            app.dataset.isUserAuthenticated === 'True' ? true : false,
        id: userId === 'None' ? -1 : Number(userId),
    },
};

switch (app.dataset.pageName) {
    case 'all_posts':
        config.page = {
            name: app.dataset.pageName,
            postApiUrl: '/posts',
        };
        break;

    case 'user_profile':
        const userId = Number(app.dataset.pageUserId);
        config.page = {
            name: app.dataset.pageName,
            postApiUrl: `/users/${userId}/posts`,
            user_id: userId,
        };
        break;

    case 'subscriptions':
        config.page = {
            name: app.dataset.pageName,
            postApiUrl: '/posts/subscriptions',
        };
        break;

    default:
        break;
}

ReactDOM.render(<App initConfig={config} />, app);
