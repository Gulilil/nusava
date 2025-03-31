import { Post } from '../utils/Types';

interface Props {
  post: Post;
}

export default function PostCard({ post }: Props) {
    return (
        <div className="border p-4 rounded shadow-sm hover:shadow-md transition">
            <img crossOrigin="anonymous"
                src={`http://localhost:8000/api/proxy-image/?url=${encodeURIComponent(post.thumbnail_url)}`}
                alt="Post"
                className="w-full mb-2 rounded" />
        <p className="text-sm mb-1">{post.caption}</p>
        <p className="text-xs text-gray-600">
            ❤️ {post.like_count} • 💬 {post.comment_count}
        </p>
        </div>
    );
}
