import PostCard from '../components/PostCard';
import { Post } from '../utils/Types';

interface Props {
  posts: Post[];
}

export default function Dashboard({ posts }: Props) {
  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">Bot Dashboard</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {posts.map(post => (
          <PostCard key={post.id} post={post} />
        ))}
      </div>
    </div>
  );
}
