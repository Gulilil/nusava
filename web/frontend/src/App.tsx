import { useState } from 'react';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import { Post } from './utils/Types';

function App() {
  const [posts, setPosts] = useState<Post[] | null>(null);

  return (
    <div className="min-h-screen bg-gray-100">
      {posts ? (
        <Dashboard posts={posts} />
      ) : (
        <Login onLogin={setPosts} />
      )}
    </div>
  );
}

export default App;
