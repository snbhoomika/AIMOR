import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { lostItemsService, foundItemsService, claimsService, notificationsService } from '../services/api';
import {
  PackageSearch,
  PackagePlus,
  FileText,
  Bell,
  TrendingUp,
  Calendar,
  ArrowRight,
  Loader2,
} from 'lucide-react';

export default function Dashboard() {
  const { user } = useAuth();
  const [stats, setStats] = useState({
    myLostItems: 0,
    myFoundItems: 0,
    pendingClaims: 0,
    unreadNotifications: 0,
  });
  const [recentItems, setRecentItems] = useState({ lost: [], found: [] });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const [lostRes, foundRes, claimsRes, notifRes] = await Promise.all([
        lostItemsService.getMy({ limit: 5 }),
        foundItemsService.getMy({ limit: 5 }),
        claimsService.getMyClaims({ status: 'pending' }),
        notificationsService.getUnreadCount(),
      ]);

      setStats({
        myLostItems: lostRes.data.length,
        myFoundItems: foundRes.data.length,
        pendingClaims: claimsRes.data.length,
        unreadNotifications: notifRes.data.unread_count,
      });

      setRecentItems({
        lost: lostRes.data.slice(0, 3),
        found: foundRes.data.slice(0, 3),
      });
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const statCards = [
    {
      title: 'My Lost Items',
      value: stats.myLostItems,
      icon: PackageSearch,
      color: 'bg-red-500',
      link: '/lost-items',
    },
    {
      title: 'My Found Items',
      value: stats.myFoundItems,
      icon: PackagePlus,
      color: 'bg-green-500',
      link: '/found-items',
    },
    {
      title: 'Pending Claims',
      value: stats.pendingClaims,
      icon: FileText,
      color: 'bg-yellow-500',
      link: '/claims',
    },
    {
      title: 'Notifications',
      value: stats.unreadNotifications,
      icon: Bell,
      color: 'bg-blue-500',
      link: '/notifications',
    },
  ];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-8 h-8 animate-spin text-primary-600" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">
          Welcome back, {user?.full_name?.split(' ')[0] || 'User'}!
        </h1>
        <p className="text-gray-600 mt-1">
          Here's what's happening with your items
        </p>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Link
          to="/lost-items/create"
          className="card hover:shadow-md transition-shadow border-l-4 border-l-red-500"
        >
          <div className="flex items-center gap-4">
            <div className="p-3 bg-red-100 rounded-xl">
              <PackageSearch className="w-6 h-6 text-red-600" />
            </div>
            <div className="flex-1">
              <h3 className="font-semibold text-gray-900">Report Lost Item</h3>
              <p className="text-sm text-gray-500">Upload details of your lost item</p>
            </div>
            <ArrowRight className="w-5 h-5 text-gray-400" />
          </div>
        </Link>

        <Link
          to="/found-items/create"
          className="card hover:shadow-md transition-shadow border-l-4 border-l-green-500"
        >
          <div className="flex items-center gap-4">
            <div className="p-3 bg-green-100 rounded-xl">
              <PackagePlus className="w-6 h-6 text-green-600" />
            </div>
            <div className="flex-1">
              <h3 className="font-semibold text-gray-900">Report Found Item</h3>
              <p className="text-sm text-gray-500">Help someone find their item</p>
            </div>
            <ArrowRight className="w-5 h-5 text-gray-400" />
          </div>
        </Link>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {statCards.map((stat) => (
          <Link
            key={stat.title}
            to={stat.link}
            className="card hover:shadow-md transition-shadow"
          >
            <div className="flex items-center gap-3">
              <div className={`p-3 rounded-xl ${stat.color}`}>
                <stat.icon className="w-5 h-5 text-white" />
              </div>
              <div>
                <p className="text-2xl font-bold text-gray-900">{stat.value}</p>
                <p className="text-sm text-gray-500">{stat.title}</p>
              </div>
            </div>
          </Link>
        ))}
      </div>

      {/* Recent Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Lost Items */}
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900">Recent Lost Items</h2>
            <Link to="/lost-items" className="text-sm text-primary-600 hover:text-primary-700">
              View All
            </Link>
          </div>

          {recentItems.lost.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <PackageSearch className="w-12 h-12 mx-auto mb-3 text-gray-300" />
              <p>No lost items reported yet</p>
              <Link to="/lost-items/create" className="text-primary-600 hover:underline text-sm">
                Report one now
              </Link>
            </div>
          ) : (
            <div className="space-y-3">
              {recentItems.lost.map((item) => (
                <Link
                  key={item.id}
                  to={`/items/lost/${item.id}`}
                  className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
                >
                  <div className="w-12 h-12 bg-red-100 rounded-lg flex items-center justify-center">
                    <PackageSearch className="w-6 h-6 text-red-600" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="font-medium text-gray-900 truncate">{item.title}</p>
                    <p className="text-sm text-gray-500">{item.category}</p>
                  </div>
                  <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                    item.status === 'active' ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-700'
                  }`}>
                    {item.status}
                  </span>
                </Link>
              ))}
            </div>
          )}
        </div>

        {/* Recent Found Items */}
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900">Recent Found Items</h2>
            <Link to="/found-items" className="text-sm text-primary-600 hover:text-primary-700">
              View All
            </Link>
          </div>

          {recentItems.found.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <PackagePlus className="w-12 h-12 mx-auto mb-3 text-gray-300" />
              <p>No found items reported yet</p>
              <Link to="/found-items/create" className="text-primary-600 hover:underline text-sm">
                Report one now
              </Link>
            </div>
          ) : (
            <div className="space-y-3">
              {recentItems.found.map((item) => (
                <Link
                  key={item.id}
                  to={`/items/found/${item.id}`}
                  className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
                >
                  <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                    <PackagePlus className="w-6 h-6 text-green-600" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="font-medium text-gray-900 truncate">{item.title}</p>
                    <p className="text-sm text-gray-500">{item.category}</p>
                  </div>
                  <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                    item.status === 'active' ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-700'
                  }`}>
                    {item.status}
                  </span>
                </Link>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Quick Search */}
      <div className="card bg-gradient-to-r from-primary-600 to-primary-700 text-white">
        <div className="flex flex-col md:flex-row items-center gap-6">
          <div className="flex-1">
            <h2 className="text-xl font-bold mb-2">Find Your Items</h2>
            <p className="text-primary-100">
              Search by image or description to find matching lost and found items
            </p>
          </div>
          <Link
            to="/search"
            className="px-6 py-3 bg-white text-primary-700 font-semibold rounded-lg hover:bg-primary-50 transition-colors"
          >
            Start Search
          </Link>
        </div>
      </div>
    </div>
  );
}
