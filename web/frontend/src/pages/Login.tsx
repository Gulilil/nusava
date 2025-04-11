import { useState } from 'react';
import { loginBot, getBotPosts } from '../api/bot';
import { Post } from '../utils/Types';

interface Props {
  onLogin: (posts: Post[]) => void;
}

export default function Login({ onLogin }: Props) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');

  const handleLogin = async () => {
    await loginBot(username, password);
    const posts = await getBotPosts();
    onLogin(posts);
  };

  return (
    <div className="flex flex-col gap-2 w-full max-w-sm mx-auto mt-20">
      <h1 className="text-xl font-bold text-center">Instagram Bot Login</h1>
      <input
        className="border p-2 rounded"
        placeholder="Username"
        value={username}
        onChange={e => setUsername(e.target.value)}
      />
      <input
        className="border p-2 rounded"
        placeholder="Password"
        type="password"
        value={password}
        onChange={e => setPassword(e.target.value)}
      />
      <button
        onClick={handleLogin}
        className="bg-blue-600 text-white p-2 rounded hover:bg-blue-700"
      >
        Login & Load Posts
      </button>
    </div>
  );
}
