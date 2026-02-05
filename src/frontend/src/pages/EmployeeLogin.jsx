import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { LogIn, User, Lock } from 'lucide-react';
import toast from 'react-hot-toast';
import { authAPI } from '../services/api';
import LoadingSpinner from '../components/LoadingSpinner';

export default function EmployeeLogin() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    name: '',
    pin: '',
  });
  const [isLoading, setIsLoading] = useState(false);
  
  // Common employee names for quick selection
  const commonNames = [
    'John Doe',
    'Jane Smith',
    'Bob Lee',
    'Alice Chen',
    'Charlie Brown',
  ];
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.name.trim()) {
      toast.error('Please enter your name');
      return;
    }
    
    if (formData.pin.length !== 4) {
      toast.error('PIN must be 4 digits');
      return;
    }
    
    setIsLoading(true);
    
    try {
      const result = await authAPI.verify(formData.name, formData.pin);
      
      if (result.success) {
        toast.success(`Welcome, ${result.employee_name}!`);
        // Store employee name in localStorage
        localStorage.setItem('employeeName', result.employee_name);
        // Navigate to time entry
        navigate('/employee/time-entry');
      } else {
        toast.error(result.message || 'Invalid credentials');
      }
    } catch (error) {
      toast.error(error.message || 'Login failed');
    } finally {
      setIsLoading(false);
    }
  };
  
  const handlePinInput = (e) => {
    const value = e.target.value.replace(/\D/g, '').slice(0, 4);
    setFormData({ ...formData, pin: value });
  };
  
  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 via-white to-primary-50 flex items-center justify-center p-4">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="w-full max-w-md"
      >
        <div className="card">
          {/* Header */}
          <div className="text-center mb-8">
            <div className="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <User className="w-8 h-8 text-primary-600" />
            </div>
            <h1 className="text-2xl font-bold text-gray-900 mb-2">
              Employee Login
            </h1>
            <p className="text-gray-600">
              Enter your name and PIN to continue
            </p>
          </div>
          
          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Name Input with Suggestions */}
            <div>
              <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-2">
                Your Name
              </label>
              <div className="relative">
                <input
                  type="text"
                  id="name"
                  list="employee-names"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="input pl-10"
                  placeholder="Type or select your name"
                  autoComplete="off"
                  disabled={isLoading}
                  required
                />
                <User className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                <datalist id="employee-names">
                  {commonNames.map((name) => (
                    <option key={name} value={name} />
                  ))}
                </datalist>
              </div>
              <p className="mt-1 text-xs text-gray-500">
                Start typing to search or select from the list
              </p>
            </div>
            
            {/* PIN Input */}
            <div>
              <label htmlFor="pin" className="block text-sm font-medium text-gray-700 mb-2">
                4-Digit PIN
              </label>
              <div className="relative">
                <input
                  type="password"
                  id="pin"
                  value={formData.pin}
                  onChange={handlePinInput}
                  className="input pl-10 text-2xl tracking-widest text-center"
                  placeholder="••••"
                  inputMode="numeric"
                  pattern="[0-9]*"
                  maxLength="4"
                  disabled={isLoading}
                  required
                />
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
              </div>
            </div>
            
            {/* Submit Button */}
            <motion.button
              type="submit"
              className="btn btn-primary w-full py-3 text-lg font-semibold flex items-center justify-center gap-2"
              disabled={isLoading || formData.pin.length !== 4}
              whileTap={{ scale: 0.98 }}
            >
              {isLoading ? (
                <LoadingSpinner size="sm" />
              ) : (
                <>
                  <LogIn className="w-5 h-5" />
                  Log In
                </>
              )}
            </motion.button>
          </form>
          
          {/* Footer */}
          <div className="mt-8 pt-6 border-t border-gray-200 text-center">
            <p className="text-sm text-gray-600">
              Are you a manager?{' '}
              <button
                onClick={() => navigate('/manager')}
                className="text-primary-600 hover:text-primary-700 font-medium"
              >
                Click here
              </button>
            </p>
          </div>
        </div>
      </motion.div>
    </div>
  );
}


