import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { foundItemsService, searchService, getImageUrl } from '../services/api';
import {
  PackagePlus,
  Plus,
  Search,
  Calendar,
  MapPin,
  Eye,
  CheckCircle,
  Loader2,
  Image as ImageIcon,
} from 'lucide-react';

export default function FoundItems() {
  const [items, setItems] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState({
    category: '',
    status: '',
    verified_only: false,
    search: '',
  });

  useEffect(() => {
    fetchCategories();
    fetchItems();
  }, [filter]);

  const fetchCategories = async () => {
    try {
      const response = await searchService.getCategories();
      setCategories(response.data.categories);
    } catch (error) {
      console.error('Failed to fetch categories:', error);
    }
  };

  const fetchItems = async () => {
    setLoading(true);
    try {
      const response = await foundItemsService.getAll({
        category: filter.category || undefined,
        status: filter.status || undefined,
        verified_only: filter.verified_only,
      });
      setItems(response.data);
    } catch (error) {
      console.error('Failed to fetch items:', error);
    } finally {
      setLoading(false);
    }
  };

  const filteredItems = items.filter((item) => {
    if (filter.search) {
      const searchLower = filter.search.toLowerCase();
      return (
        item.title.toLowerCase().includes(searchLower) ||
        item.description.toLowerCase().includes(searchLower)
      );
    }
    return true;
  });

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  };

  const statusColors = {
    active: 'bg-green-100 text-green-700',
    matched: 'bg-yellow-100 text-yellow-700',
    claimed: 'bg-blue-100 text-blue-700',
    returned: 'bg-purple-100 text-purple-700',
    expired: 'bg-gray-100 text-gray-700',
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Found Items</h1>
          <p className="text-gray-600">Help reunite items with their owners</p>
        </div>
        <Link to="/found-items/create" className="btn-primary flex items-center gap-2">
          <Plus className="w-5 h-5" />
          Report Found Item
        </Link>
      </div>

      {/* Filters */}
      <div className="card">
        <div className="flex flex-col md:flex-row gap-4 flex-wrap">
          <div className="flex-1 min-w-[200px]">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                placeholder="Search by title or description..."
                className="input-field pl-10"
                value={filter.search}
                onChange={(e) => setFilter({ ...filter, search: e.target.value })}
              />
            </div>
          </div>
          <select
            className="input-field md:w-48"
            value={filter.category}
            onChange={(e) => setFilter({ ...filter, category: e.target.value })}
          >
            <option value="">All Categories</option>
            {categories.map((cat) => (
              <option key={cat.value} value={cat.value}>
                {cat.label}
              </option>
            ))}
          </select>
          <select
            className="input-field md:w-40"
            value={filter.status}
            onChange={(e) => setFilter({ ...filter, status: e.target.value })}
          >
            <option value="">All Status</option>
            <option value="active">Active</option>
            <option value="matched">Matched</option>
            <option value="returned">Returned</option>
          </select>
          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              checked={filter.verified_only}
              onChange={(e) => setFilter({ ...filter, verified_only: e.target.checked })}
              className="w-4 h-4 rounded border-gray-300 text-primary-600 focus:ring-primary-500"
            />
            <span className="text-sm text-gray-700">Verified only</span>
          </label>
        </div>
      </div>

      {/* Items Grid */}
      {loading ? (
        <div className="flex items-center justify-center h-64">
          <Loader2 className="w-8 h-8 animate-spin text-primary-600" />
        </div>
      ) : filteredItems.length === 0 ? (
        <div className="card text-center py-12">
          <PackagePlus className="w-16 h-16 mx-auto mb-4 text-gray-300" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No items found</h3>
          <p className="text-gray-500 mb-4">
            {filter.search || filter.category || filter.status
              ? 'Try adjusting your filters'
              : 'Help others by reporting found items'}
          </p>
          <Link to="/found-items/create" className="btn-primary">
            Report Found Item
          </Link>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredItems.map((item) => (
            <Link
              key={item.id}
              to={`/items/found/${item.id}`}
              className="card hover:shadow-lg transition-shadow"
            >
              <div className="aspect-video bg-gray-100 rounded-lg mb-4 overflow-hidden relative">
                {item.images && item.images.length > 0 ? (
                  <img
                    src={getImageUrl(item.images[0])}
                    alt={item.title}
                    className="w-full h-full object-cover"
                    onError={(e) => {
                      e.target.style.display = 'none';
                    }}
                  />
                ) : (
                  <div className="w-full h-full flex items-center justify-center">
                    <ImageIcon className="w-12 h-12 text-gray-300" />
                  </div>
                )}
                {item.is_verified && (
                  <div className="absolute top-2 right-2 bg-green-500 text-white px-2 py-1 rounded-full text-xs font-medium flex items-center gap-1">
                    <CheckCircle className="w-3 h-3" />
                    Verified
                  </div>
                )}
              </div>

              <div className="space-y-2">
                <div className="flex items-start justify-between gap-2">
                  <h3 className="font-semibold text-gray-900 line-clamp-1">{item.title}</h3>
                  <span className={`px-2 py-1 text-xs font-medium rounded-full ${statusColors[item.status]}`}>
                    {item.status}
                  </span>
                </div>

                <p className="text-sm text-gray-600 line-clamp-2">{item.description}</p>

                <div className="flex items-center gap-4 text-sm text-gray-500">
                  <span className="flex items-center gap-1">
                    <Calendar className="w-4 h-4" />
                    {formatDate(item.date)}
                  </span>
                  {item.current_location && (
                    <span className="flex items-center gap-1">
                      <MapPin className="w-4 h-4" />
                      {item.current_location?.split(',')[0]}
                    </span>
                  )}
                </div>

                <div className="flex items-center gap-4 pt-2 border-t border-gray-100">
                  <span className="text-sm text-gray-500">
                    Category: <span className="font-medium text-gray-700 capitalize">{item.category}</span>
                  </span>
                  <span className="flex items-center gap-1 text-sm text-gray-500">
                    <Eye className="w-4 h-4" />
                    {item.views}
                  </span>
                </div>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
