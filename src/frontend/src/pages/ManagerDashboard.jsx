import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { DollarSign, Users, LogOut, Calendar, TrendingUp, Shield } from 'lucide-react';
import toast from 'react-hot-toast';
import { managerAPI } from '../services/api';
import { getCurrentDate } from '../utils/timeCalculator';
import LoadingSpinner from '../components/LoadingSpinner';

export default function ManagerDashboard() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    date: getCurrentDate(),
    total_tips: '',
  });
  const [isLoading, setIsLoading] = useState(false);
  const [employees, setEmployees] = useState([]);
  
  useEffect(() => {
    // Check manager auth
    const isAuth = localStorage.getItem('managerAuth');
    if (!isAuth) {
      toast.error('Please log in first');
      navigate('/manager');
      return;
    }
    
    // Load employees
    loadEmployees();
  }, [navigate]);
  
  const loadEmployees = async () => {
    try {
      const data = await managerAPI.getEmployees();
      setEmployees(data);
    } catch (error) {
      console.error('Failed to load employees:', error);
    }
  };
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.total_tips || parseFloat(formData.total_tips) <= 0) {
      toast.error('Please enter a valid tip amount');
      return;
    }
    
    setIsLoading(true);
    
    try {
      const result = await managerAPI.submitTips({
        date: formData.date,
        total_tips: parseFloat(formData.total_tips),
      });
      
      if (result.success) {
        toast.success(
          result.formulas_injected
            ? `Tips submitted! Formulas calculated for ${result.message.match(/\d+/)?.[0] || 'all'} employees.`
            : 'Tips submitted successfully!',
          { duration: 4000 }
        );
        // Reset form
        setFormData({
          date: getCurrentDate(),
          total_tips: '',
        });
      }
    } catch (error) {
      toast.error(error.message || 'Failed to submit tips');
    } finally {
      setIsLoading(false);
    }
  };
  
  const handleLogout = () => {
    localStorage.removeItem('managerAuth');
    toast.success('Logged out successfully');
    navigate('/manager');
  };
  
  return (
    <div className="min-h-screen bg-gradient-to-br from-amber-50 via-white to-amber-50 p-4">
      <div className="max-w-6xl mx-auto py-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8"
        >
          <div>
            <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
              <Shield className="w-8 h-8 text-amber-600" />
              Manager Dashboard
            </h1>
            <p className="text-gray-600 mt-1">
              Submit daily tips and manage employees
            </p>
          </div>
          <button
            onClick={handleLogout}
            className="btn btn-secondary flex items-center gap-2"
          >
            <LogOut className="w-4 h-4" />
            Logout
          </button>
        </motion.div>
        
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Daily Tip Input */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.1 }}
          >
            <div className="card">
              <div className="flex items-center gap-3 mb-6">
                <div className="w-12 h-12 bg-amber-100 rounded-lg flex items-center justify-center">
                  <DollarSign className="w-6 h-6 text-amber-600" />
                </div>
                <div>
                  <h2 className="text-xl font-bold text-gray-900">
                    Submit Daily Tips
                  </h2>
                  <p className="text-sm text-gray-600">
                    Enter total tips collected for the day
                  </p>
                </div>
              </div>
              
              <form onSubmit={handleSubmit} className="space-y-4">
                {/* Date Input */}
                <div>
                  <label htmlFor="date" className="block text-sm font-medium text-gray-700 mb-2">
                    Date
                  </label>
                  <div className="relative">
                    <input
                      type="date"
                      id="date"
                      value={formData.date}
                      onChange={(e) => setFormData({ ...formData, date: e.target.value })}
                      className="input pl-10"
                      max={getCurrentDate()}
                      disabled={isLoading}
                      required
                    />
                    <Calendar className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                  </div>
                </div>
                
                {/* Total Tips Input */}
                <div>
                  <label htmlFor="total_tips" className="block text-sm font-medium text-gray-700 mb-2">
                    Total Tips Amount
                  </label>
                  <div className="relative">
                    <input
                      type="number"
                      id="total_tips"
                      value={formData.total_tips}
                      onChange={(e) => setFormData({ ...formData, total_tips: e.target.value })}
                      className="input pl-10 text-lg"
                      placeholder="0.00"
                      step="0.01"
                      min="0"
                      disabled={isLoading}
                      required
                    />
                    <DollarSign className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                  </div>
                </div>
                
                {/* Preview */}
                {formData.total_tips && parseFloat(formData.total_tips) > 0 && (
                  <motion.div
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    className="p-4 bg-amber-50 border border-amber-200 rounded-lg"
                  >
                    <p className="text-sm text-amber-900 mb-1 font-medium">
                      Preview
                    </p>
                    <p className="text-2xl font-bold text-amber-900">
                      ${parseFloat(formData.total_tips).toFixed(2)}
                    </p>
                    <p className="text-xs text-amber-700 mt-1">
                      This will be distributed among employees based on hours worked
                    </p>
                  </motion.div>
                )}
                
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
                      <TrendingUp className="w-5 h-5" />
                      Calculate & Submit
                    </>
                  )}
                </motion.button>
              </form>
            </div>
          </motion.div>
          
          {/* Employee List */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2 }}
          >
            <div className="card">
              <div className="flex items-center gap-3 mb-6">
                <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center">
                  <Users className="w-6 h-6 text-primary-600" />
                </div>
                <div>
                  <h2 className="text-xl font-bold text-gray-900">
                    Employee List
                  </h2>
                  <p className="text-sm text-gray-600">
                    Current employees from Settings sheet
                  </p>
                </div>
              </div>
              
              {employees.length > 0 ? (
                <div className="space-y-2">
                  {employees.map((employee, index) => (
                    <div
                      key={index}
                      className="p-3 bg-gray-50 rounded-lg flex items-center gap-3"
                    >
                      <div className="w-10 h-10 bg-primary-100 rounded-full flex items-center justify-center">
                        <span className="text-primary-600 font-medium">
                          {employee.name.charAt(0)}
                        </span>
                      </div>
                      <div>
                        <p className="font-medium text-gray-900">{employee.name}</p>
                        <p className="text-xs text-gray-600">PIN: ••••</p>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-12">
                  <Users className="w-12 h-12 text-gray-300 mx-auto mb-3" />
                  <p className="text-gray-600">
                    Employee list will appear here
                  </p>
                  <p className="text-sm text-gray-500 mt-1">
                    Employees are managed in the Google Sheets "Settings" tab
                  </p>
                </div>
              )}
            </div>
          </motion.div>
        </div>
        
        {/* Info Box */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.4 }}
          className="mt-6 p-4 bg-amber-50 border border-amber-200 rounded-lg"
        >
          <p className="text-sm text-amber-900">
            <strong>How it works:</strong> When you submit daily tips, the system automatically calculates the tip rate per hour and distributes tips among employees based on their submitted hours.
          </p>
        </motion.div>
      </div>
    </div>
  );
}


