import { useState, useEffect, useCallback } from 'react';
import api from '../api/api';
import { useAuth } from '../context/AuthContext';

export default function PostsPage() {
  const { user } = useAuth();
  const [posts, setPosts] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [error, setError] = useState('');
  const [editing, setEditing] = useState(null);
  const [form, setForm] = useState({ title: '', content: '' });
  const [commentText, setCommentText] = useState({});
  const limit = 5;

  const fetchPosts = useCallback(async () => {
    try {
      const res = await api.get('/posts', { params: { page, limit } });
      setPosts(res.data.data);
      setTotal(res.data.total);
    } catch (err) {
      setError('Failed to load posts');
    }
  }, [page]);

  useEffect(() => {
    fetchPosts();
  }, [fetchPosts]);

  const handleCreate = async (e) => {
    e.preventDefault();
    try {
      await api.post('/posts', form);
      setForm({ title: '', content: '' });
      fetchPosts();
    } catch (err) {
      setError(err.response?.data?.detail || 'Error creating post');
    }
  };

  const handleUpdate = async (e) => {
    e.preventDefault();
    try {
      await api.put(`/posts/${editing.id}`, form);
      setEditing(null);
      setForm({ title: '', content: '' });
      fetchPosts();
    } catch (err) {
      setError(err.response?.data?.detail || 'Error updating post');
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Delete this post?')) return;
    try {
      await api.delete(`/posts/${id}`);
      fetchPosts();
    } catch (err) {
      setError('Error deleting post');
    }
  };

  const handleAddComment = async (postId) => {
    const text = commentText[postId];
    if (!text) return;
    try {
      await api.post('/comments', { text, post_id: postId });
      setCommentText({ ...commentText, [postId]: '' });
      fetchPosts();
    } catch (err) {
      setError(err.response?.data?.detail || 'Error adding comment');
    }
  };

  const startEdit = (post) => {
    setEditing(post.id);
    setForm({ title: post.title, content: post.content || '' });
  };

  const totalPages = Math.ceil(total / limit);

  return (
    <div>
      <h2 style={{ marginBottom: 20 }}>Posts</h2>

      {error && <div className="error" onClick={() => setError('')}>{error}</div>}

      <div className="card">
        <h3 style={{ marginBottom: 12 }}>
          {editing ? 'Edit Post' : 'Create Post'}
        </h3>
        <form onSubmit={editing ? handleUpdate : handleCreate}>
          <div className="form-group">
            <label>Title</label>
            <input
              type="text"
              value={form.title}
              onChange={(e) => setForm({ ...form, title: e.target.value })}
              required
            />
          </div>
          <div className="form-group">
            <label>Content</label>
            <textarea
              rows={3}
              value={form.content}
              onChange={(e) => setForm({ ...form, content: e.target.value })}
            />
          </div>
          <div style={{ display: 'flex', gap: 8 }}>
            <button type="submit" className="btn btn-primary">
              {editing ? 'Update' : 'Create'}
            </button>
            {editing && (
              <button
                type="button"
                className="btn"
                onClick={() => {
                  setEditing(null);
                  setForm({ title: '', content: '' });
                }}
              >
                Cancel
              </button>
            )}
          </div>
        </form>
      </div>

      <div className="card">
        {posts.length === 0 ? (
          <div className="empty">No posts found</div>
        ) : (
          <>
            <table>
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Title</th>
                  <th>Content</th>
                  <th>Comments</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {posts.map((p) => (
                  <tr key={p.id}>
                    <td>{p.id}</td>
                    <td>{p.title}</td>
                    <td style={{ maxWidth: 200, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                      {p.content || '—'}
                    </td>
                    <td>
                      {p.comments?.map((c) => (
                        <div key={c.id} style={{ fontSize: 12, color: '#666' }}>
                          {c.text}
                        </div>
                      ))}
                      <div style={{ display: 'flex', gap: 4, marginTop: 4 }}>
                        <input
                          type="text"
                          placeholder="Add comment..."
                          value={commentText[p.id] || ''}
                          onChange={(e) =>
                            setCommentText({ ...commentText, [p.id]: e.target.value })
                          }
                          style={{ flex: 1, padding: '4px 8px', fontSize: 12, border: '1px solid #ddd', borderRadius: 4 }}
                        />
                        <button
                          className="btn btn-primary btn-sm"
                          onClick={() => handleAddComment(p.id)}
                        >
                          +
                        </button>
                      </div>
                    </td>
                    <td className="actions">
                      <button
                        className="btn btn-primary btn-sm"
                        onClick={() => startEdit(p)}
                      >
                        Edit
                      </button>
                      <button
                        className="btn btn-danger btn-sm"
                        onClick={() => handleDelete(p.id)}
                      >
                        Delete
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            <div className="pagination">
              <button
                className="btn btn-sm"
                disabled={page <= 1}
                onClick={() => setPage((p) => p - 1)}
              >
                Prev
              </button>
              <span>
                Page {page} of {totalPages || 1} (total: {total})
              </span>
              <button
                className="btn btn-sm"
                disabled={page >= totalPages}
                onClick={() => setPage((p) => p + 1)}
              >
                Next
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
