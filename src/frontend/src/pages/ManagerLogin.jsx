import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Shield, Lock, ArrowLeft } from 'lucide-react';
import toast from 'react-hot-toast';
import LoadingSpinner from '../components/LoadingSpinner';
import { managerAPI } from '../services/api';

export default function ManagerLogin() {
  const navigate = useNavigate();
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!password) {
      toast.error('Please enter password');
      return;
    }
    
    setIsLoading(true);
    
    try {
      const response = await managerAPI.login(password);
      
      if (response.success && response.token) {
        toast.success('Manager access granted');
        localStorage.setItem('managerAuth', 'true');
        localStorage.setItem('managerToken', response.token);
        navigate('/manager/dashboard');
      } else {
        toast.error(response.message || 'Incorrect password');
        setPassword('');
      }
    } catch (error) {
      toast.error(error.message || 'Authentication failed');
      setPassword('');
    } finally {
      setIsLoading(false);
    }
  };
  
  return (
    <div className="min-h-screen bg-gradient-to-br from-amber-50 via-white to-amber-50 flex items-center justify-center p-4">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="w-full max-w-md"
      >
        {/* Back Button */}
        <button
          onClick={() => navigate('/')}
          className="mb-4 text-gray-600 hover:text-gray-900 flex items-center gap-2 transition"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to Employee Login
        </button>
        
        <div className="card">
          {/* Header */}
          <div className="text-center mb-8">
            <div className="w-16 h-16 bg-amber-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <Shield className="w-8 h-8 text-amber-600" />
            </div>
            <h1 className="text-2xl font-bold text-gray-900 mb-2">
              Manager Access
            </h1>
            <p className="text-gray-600">
              Enter manager password to continue
            </p>
          </div>
          
          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Password Input */}
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-2">
                Password
              </label>
              <div className="relative">
                <input
                  type="password"
                  id="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="input pl-10"
                  placeholder="Enter manager password"
                  disabled={isLoading}
                  required
                  autoFocus
                />
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
              </div>
            </div>
            
            {/* Submit Button */}
            <motion.button
              type="submit"
              className="btn btn-primary w-full py-3 text-lg font-semibold flex items-center justify-center gap-2 bg-amber-600 hover:bg-amber-700 focus:ring-amber-500"
              disabled={isLoading}
              whileTap={{ scale: 0.98 }}
            >
              {isLoading ? (
                <LoadingSpinner size="sm" />
              ) : (
                <>
                  <Shield className="w-5 h-5" />
                  Access Manager Dashboard
                </>
              )}
            </motion.button>
          </form>
          
          {/* Demo Info */}
          <div className="mt-6 p-3 bg-amber-50 border border-amber-200 rounded-lg">
            <p className="text-xs text-amber-900">
              <strong>Demo:</strong> Use password <code className="bg-amber-100 px-1 py-0.5 rounded">manager2024</code>
            </p>
          </div>
        </div>
      </motion.div>
    </div>
  );
}


