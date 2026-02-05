import { Loader2 } from 'lucide-react';

/**
 * Loading spinner component
 * @param {Object} props
 * @param {string} props.size - Size: 'sm', 'md', 'lg'
 * @param {string} props.message - Optional loading message
 */
export default function LoadingSpinner({ size = 'md', message }) {
  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-8 h-8',
    lg: 'w-12 h-12',
  };
  
  return (
    <div className="flex flex-col items-center justify-center gap-3">
      <Loader2 className={`${sizeClasses[size]} text-primary-600 animate-spin`} />
      {message && (
        <p className="text-sm text-gray-600">{message}</p>
      )}
    </div>
  );
}


