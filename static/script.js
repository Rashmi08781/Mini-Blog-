async function fetchPosts() {
    const res = await fetch("/api/posts");
    const posts = await res.json();
    const container = document.getElementById("posts");
    container.innerHTML = "";
    posts.forEach(p => {
        const div = document.createElement("div");
        div.className = "post";
        div.innerHTML = `<b>${p.title}</b> by ${p.author}<br>${p.content}<br>
                         Tags: ${p.tags.join(", ")}<br>
                         Published: ${p.published}<br>
                         <button onclick="deletePost(${p.id})">Delete</button>`;
        container.appendChild(div);
    });
}

async function createPost() {
    const post = {
        title: document.getElementById("title").value,
        content: document.getElementById("content").value,
        author: document.getElementById("author").value,
        tags: document.getElementById("tags").value.split(",").map(t=>t.trim()),
        published: document.getElementById("published").checked
    };
    await fetch("/api/posts", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(post)
    });
    fetchPosts();
}

async function deletePost(id) {
    await fetch("/api/posts/" + id, { method: "DELETE" });
    fetchPosts();
}

// Load posts on page load
fetchPosts();
