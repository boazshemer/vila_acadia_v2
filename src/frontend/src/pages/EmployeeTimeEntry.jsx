import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Clock, Calendar, LogOut, Check, AlertCircle } from 'lucide-react';
import toast from 'react-hot-toast';
import { hoursAPI } from '../services/api';
import { calculateHours, getCurrentDate, getCurrentTime } from '../utils/timeCalculator';
import LoadingSpinner from '../components/LoadingSpinner';

export default function EmployeeTimeEntry() {
  const navigate = useNavigate();
  const [employeeName, setEmployeeName] = useState('');
  const [formData, setFormData] = useState({
    date: getCurrentDate(),
    start_time: '',
    end_time: '',
  });
  const [calculatedHours, setCalculatedHours] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  
  useEffect(() => {
    // Get employee name from localStorage
    const name = localStorage.getItem('employeeName');
    if (!name) {
      toast.error('Please log in first');
      navigate('/');
      return;
    }
    setEmployeeName(name);
  }, [navigate]);
  
  useEffect(() => {
    // Auto-calculate hours when times change
    const hours = calculateHours(formData.start_time, formData.end_time);
    setCalculatedHours(hours);
  }, [formData.start_time, formData.end_time]);
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.start_time || !formData.end_time) {
      toast.error('Please enter both start and end times');
      return;
    }
    
    if (calculatedHours === 0) {
      toast.error('Invalid time range');
      return;
    }
    
    setIsLoading(true);
    
    try {
      const result = await hoursAPI.submit({
        employee_name: employeeName,
        date: formData.date,
        start_time: formData.start_time,
        end_time: formData.end_time,
      });
      
      if (result.success) {
        toast.success(
          `Successfully submitted ${result.hours_worked} hours for ${result.date}`,
          { duration: 4000 }
        );
        // Reset form
        setFormData({
          date: getCurrentDate(),
          start_time: '',
          end_time: '',
        });
      }
    } catch (error) {
      toast.error(error.message || 'Failed to submit hours');
    } finally {
      setIsLoading(false);
    }
  };
  
  const handleLogout = () => {
    localStorage.removeItem('employeeName');
    toast.success('Logged out successfully');
    navigate('/');
  };
  
  const setQuickTime = (type, time) => {
    setFormData({ ...formData, [type]: time });
  };
  
  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 via-white to-primary-50 p-4">
      <div className="max-w-2xl mx-auto py-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex items-center justify-between mb-8"
        >
          <div>
            <h1 className="text-2xl font-bold text-gray-900">
              Submit Hours
            </h1>
            <p className="text-gray-600 mt-1">
              Welcome, {employeeName}!
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
        
        {/* Main Card */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="card"
        >
          <form onSubmit={handleSubmit} className="space-y-6">
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
            
            {/* Time Inputs */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Start Time */}
              <div>
                <label htmlFor="start_time" className="block text-sm font-medium text-gray-700 mb-2">
                  Start Time
                </label>
                <div className="relative">
                  <input
                    type="time"
                    id="start_time"
                    value={formData.start_time}
                    onChange={(e) => setFormData({ ...formData, start_time: e.target.value })}
                    className="input pl-10"
                    disabled={isLoading}
                    required
                  />
                  <Clock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                </div>
                {/* Quick Time Buttons */}
                <div className="flex gap-2 mt-2">
                  <button
                    type="button"
                    onClick={() => setQuickTime('start_time', '09:00')}
                    className="text-xs px-2 py-1 bg-gray-100 hover:bg-gray-200 rounded transition"
                  >
                    9 AM
                  </button>
                  <button
                    type="button"
                    onClick={() => setQuickTime('start_time', '17:00')}
                    className="text-xs px-2 py-1 bg-gray-100 hover:bg-gray-200 rounded transition"
                  >
                    5 PM
                  </button>
                  <button
                    type="button"
                    onClick={() => setQuickTime('start_time', getCurrentTime())}
                    className="text-xs px-2 py-1 bg-gray-100 hover:bg-gray-200 rounded transition"
                  >
                    Now
                  </button>
                </div>
              </div>
              
              {/* End Time */}
              <div>
                <label htmlFor="end_time" className="block text-sm font-medium text-gray-700 mb-2">
                  End Time
                </label>
                <div className="relative">
                  <input
                    type="time"
                    id="end_time"
                    value={formData.end_time}
                    onChange={(e) => setFormData({ ...formData, end_time: e.target.value })}
                    className="input pl-10"
                    disabled={isLoading}
                    required
                  />
                  <Clock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                </div>
                {/* Quick Time Buttons */}
                <div className="flex gap-2 mt-2">
                  <button
                    type="button"
                    onClick={() => setQuickTime('end_time', '17:00')}
                    className="text-xs px-2 py-1 bg-gray-100 hover:bg-gray-200 rounded transition"
                  >
                    5 PM
                  </button>
                  <button
                    type="button"
                    onClick={() => setQuickTime('end_time', '23:00')}
                    className="text-xs px-2 py-1 bg-gray-100 hover:bg-gray-200 rounded transition"
                  >
                    11 PM
                  </button>
                  <button
                    type="button"
                    onClick={() => setQuickTime('end_time', getCurrentTime())}
                    className="text-xs px-2 py-1 bg-gray-100 hover:bg-gray-200 rounded transition"
                  >
                    Now
                  </button>
                </div>
              </div>
            </div>
            
            {/* Calculated Hours Display */}
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className={`p-6 rounded-xl border-2 ${
                calculatedHours > 0
                  ? 'bg-primary-50 border-primary-200'
                  : 'bg-gray-50 border-gray-200'
              }`}
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600 mb-1">
                    Total Hours
                  </p>
                  <div className="flex items-baseline gap-2">
                    <span className="text-4xl font-bold text-gray-900">
                      {calculatedHours.toFixed(2)}
                    </span>
                    <span className="text-lg text-gray-600">hours</span>
                  </div>
                </div>
                <div className={`w-12 h-12 rounded-full flex items-center justify-center ${
                  calculatedHours > 0 ? 'bg-primary-100' : 'bg-gray-200'
                }`}>
                  <Clock className={`w-6 h-6 ${
                    calculatedHours > 0 ? 'text-primary-600' : 'text-gray-400'
                  }`} />
                </div>
              </div>
              
              {calculatedHours > 12 && (
                <div className="mt-3 flex items-start gap-2 text-sm text-amber-700">
                  <AlertCircle className="w-4 h-4 mt-0.5 flex-shrink-0" />
                  <span>
                    This appears to be an overnight shift ({calculatedHours} hours)
                  </span>
                </div>
              )}
            </motion.div>
            
            {/* Submit Button */}
            <motion.button
              type="submit"
              className="btn btn-primary w-full py-4 text-lg font-semibold flex items-center justify-center gap-2"
              disabled={isLoading || calculatedHours === 0}
              whileTap={{ scale: 0.98 }}
            >
              {isLoading ? (
                <LoadingSpinner size="sm" />
              ) : (
                <>
                  <Check className="w-5 h-5" />
                  Submit Hours
                </>
              )}
            </motion.button>
          </form>
        </motion.div>
        
        {/* Info Box */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3 }}
          className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg"
        >
          <p className="text-sm text-blue-900">
            <strong>Note:</strong> You can only submit hours once per day. Make sure the times are correct before submitting.
          </p>
        </motion.div>
      </div>
    </div>
  );
}


