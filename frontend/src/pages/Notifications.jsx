import { useState, useEffect } from 'react';
import { notificationsService } from '../services/api';
import {
  Bell,
  Check,
  CheckCheck,
  Trash2,
  PackageSearch,
  PackagePlus,
  FileText,
  AlertCircle,
  Loader2,
} from 'lucide-react';

export default function Notifications() {
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [unreadOnly, setUnreadOnly] = useState(false);

  useEffect(() => {
    fetchNotifications();
  }, [unreadOnly]);

  const fetchNotifications = async () => {
    setLoading(true);
    try {
      const response = await notificationsService.getAll({
        unread_only: unreadOnly,
        limit: 50,
      });
      setNotifications(response.data);
    } catch (error) {
      console.error('Failed to fetch notifications:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleMarkAsRead = async (id) => {
    try {
      await notificationsService.markAsRead(id);
      fetchNotifications();
    } catch (error) {
      console.error('Failed to mark as read:', error);
    }
  };

  const handleMarkAllAsRead = async () => {
    try {
      await notificationsService.markAllAsRead();
      fetchNotifications();
    } catch (error) {
      console.error('Failed to mark all as read:', error);
    }
  };

  const handleDelete = async (id) => {
    try {
      await notificationsService.delete(id);
      fetchNotifications();
    } catch (error) {
      console.error('Failed to delete notification:', error);
    }
  };

  const handleClearAll = async () => {
    if (confirm('Are you sure you want to delete all notifications?')) {
      try {
        await notificationsService.clearAll();
        fetchNotifications();
      } catch (error) {
        console.error('Failed to clear all:', error);
      }
    }
  };

  const getNotificationIcon = (type) => {
    switch (type) {
      case 'match_found':
        return PackageSearch;
      case 'claim_received':
        return FileText;
      case 'claim_accepted':
        return Check;
      case 'claim_rejected':
        return AlertCircle;
      case 'item_returned':
        return PackagePlus;
      default:
        return Bell;
    }
  };

  const getNotificationColor = (type) => {
    switch (type) {
      case 'match_found':
        return 'bg-blue-100 text-blue-600';
      case 'claim_received':
        return 'bg-purple-100 text-purple-600';
      case 'claim_accepted':
        return 'bg-green-100 text-green-600';
      case 'claim_rejected':
        return 'bg-red-100 text-red-600';
      case 'item_returned':
        return 'bg-yellow-100 text-yellow-600';
      default:
        return 'bg-gray-100 text-gray-600';
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const diff = now - date;
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);

    if (minutes < 1) return 'Just now';
    if (minutes < 60) return `${minutes}m ago`;
    if (hours < 24) return `${hours}h ago`;
    if (days < 7) return `${days}d ago`;
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Notifications</h1>
          <p className="text-gray-600">Stay updated on your items and claims</p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={handleMarkAllAsRead}
            className="btn-secondary flex items-center gap-2"
          >
            <CheckCheck className="w-4 h-4" />
            Mark All Read
          </button>
          <button
            onClick={handleClearAll}
            className="btn-danger flex items-center gap-2"
          >
            <Trash2 className="w-4 h-4" />
            Clear All
          </button>
        </div>
      </div>

      {/* Filter */}
      <div className="card">
        <label className="flex items-center gap-2 cursor-pointer">
          <input
            type="checkbox"
            checked={unreadOnly}
            onChange={(e) => setUnreadOnly(e.target.checked)}
            className="w-4 h-4 rounded border-gray-300 text-primary-600 focus:ring-primary-500"
          />
          <span className="text-sm text-gray-700">Show unread only</span>
        </label>
      </div>

      {/* Notifications List */}
      {loading ? (
        <div className="flex items-center justify-center h-64">
          <Loader2 className="w-8 h-8 animate-spin text-primary-600" />
        </div>
      ) : notifications.length === 0 ? (
        <div className="card text-center py-12">
          <Bell className="w-16 h-16 mx-auto mb-4 text-gray-300" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            {unreadOnly ? 'No unread notifications' : 'No notifications'}
          </h3>
          <p className="text-gray-500">
            {unreadOnly
              ? 'You have read all your notifications'
              : 'Notifications about your items and claims will appear here'}
          </p>
        </div>
      ) : (
        <div className="space-y-2">
          {notifications.map((notification) => {
            const Icon = getNotificationIcon(notification.type);
            const colorClass = getNotificationColor(notification.type);

            return (
              <div
                key={notification.id}
                className={`card flex items-start gap-4 ${
                  !notification.read ? 'bg-primary-50 border-l-4 border-l-primary-600' : ''
                }`}
              >
                <div className={`p-2 rounded-lg ${colorClass}`}>
                  <Icon className="w-5 h-5" />
                </div>

                <div className="flex-1 min-w-0">
                  <div className="flex items-start justify-between gap-2">
                    <div>
                      <h4 className="font-medium text-gray-900">{notification.title}</h4>
                      <p className="text-sm text-gray-600 mt-1">{notification.message}</p>
                    </div>
                    {!notification.read && (
                      <span className="w-2 h-2 bg-primary-600 rounded-full flex-shrink-0 mt-2" />
                    )}
                  </div>

                  <div className="flex items-center justify-between mt-3">
                    <span className="text-xs text-gray-500">
                      {formatDate(notification.created_at)}
                    </span>
                    <div className="flex gap-2">
                      {!notification.read && (
                        <button
                          onClick={() => handleMarkAsRead(notification.id)}
                          className="text-sm text-primary-600 hover:text-primary-700"
                        >
                          Mark as read
                        </button>
                      )}
                      <button
                        onClick={() => handleDelete(notification.id)}
                        className="text-sm text-red-600 hover:text-red-700"
                      >
                        Delete
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
