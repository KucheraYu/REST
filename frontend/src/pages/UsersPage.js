import { useState, useEffect, useCallback } from 'react';
import api from '../api/api';

export default function UsersPage() {
  const [users, setUsers] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [error, setError] = useState('');
  const [editing, setEditing] = useState(null);
  const [form, setForm] = useState({ name: '', email: '', password: '' });
  const limit = 5;

  const fetchUsers = useCallback(async () => {
    try {
      const res = await api.get('/users', { params: { page, limit } });
      setUsers(res.data.data);
      setTotal(res.data.total);
    } catch (err) {
      setError('Failed to load users');
    }
  }, [page]);

  useEffect(() => {
    fetchUsers();
  }, [fetchUsers]);

  const handleCreate = async (e) => {
    e.preventDefault();
    try {
      await api.post('/users', form);
      setForm({ name: '', email: '', password: '' });
      fetchUsers();
    } catch (err) {
      setError(err.response?.data?.detail || 'Error creating user');
    }
  };

  const handleUpdate = async (e) => {
    e.preventDefault();
    try {
      await api.put(`/users/${editing.id}`, {
        name: form.name,
        email: form.email,
        ...(form.password ? { password: form.password } : {}),
      });
      setEditing(null);
      setForm({ name: '', email: '', password: '' });
      fetchUsers();
    } catch (err) {
      setError(err.response?.data?.detail || 'Error updating user');
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Delete this user?')) return;
    try {
      await api.delete(`/users/${id}`);
      fetchUsers();
    } catch (err) {
      setError('Error deleting user');
    }
  };

  const startEdit = (user) => {
    setEditing(user.id);
    setForm({ name: user.name, email: user.email, password: '' });
  };

  const totalPages = Math.ceil(total / limit);

  return (
    <div>
      <h2 style={{ marginBottom: 20 }}>Users</h2>

      {error && <div className="error" onClick={() => setError('')}>{error}</div>}

      <div className="card">
        <h3 style={{ marginBottom: 12 }}>
          {editing ? 'Edit User' : 'Create User'}
        </h3>
        <form onSubmit={editing ? handleUpdate : handleCreate}>
          <div className="form-group">
            <label>Name</label>
            <input
              type="text"
              value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
              required
            />
          </div>
          <div className="form-group">
            <label>Email</label>
            <input
              type="email"
              value={form.email}
              onChange={(e) => setForm({ ...form, email: e.target.value })}
              required
            />
          </div>
          <div className="form-group">
            <label>Password {editing && '(leave empty to keep)'}</label>
            <input
              type="password"
              value={form.password}
              onChange={(e) => setForm({ ...form, password: e.target.value })}
              required={!editing}
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
                  setForm({ name: '', email: '', password: '' });
                }}
              >
                Cancel
              </button>
            )}
          </div>
        </form>
      </div>

      <div className="card">
        {users.length === 0 ? (
          <div className="empty">No users found</div>
        ) : (
          <>
            <table>
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Name</th>
                  <th>Email</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {users.map((u) => (
                  <tr key={u.id}>
                    <td>{u.id}</td>
                    <td>{u.name}</td>
                    <td>{u.email}</td>
                    <td className="actions">
                      <button
                        className="btn btn-primary btn-sm"
                        onClick={() => startEdit(u)}
                      >
                        Edit
                      </button>
                      <button
                        className="btn btn-danger btn-sm"
                        onClick={() => handleDelete(u.id)}
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
