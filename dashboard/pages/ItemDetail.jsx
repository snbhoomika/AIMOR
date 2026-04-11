import { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { lostItemsService, foundItemsService, claimsService, searchService, getImageUrl } from '../services/api';
import { useAuth } from '../context/AuthContext';
import {
  ArrowLeft,
  Calendar,
  MapPin,
  Eye,
  PackageSearch,
  PackagePlus,
  Image as ImageIcon,
  CheckCircle,
  Loader2,
  AlertCircle,
  MessageSquare,
} from 'lucide-react';

export default function ItemDetail() {
  const { type, id } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const [item, setItem] = useState(null);
  const [matches, setMatches] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showClaimModal, setShowClaimModal] = useState(false);
  const [claimMessage, setClaimMessage] = useState('');
  const [claimLoading, setClaimLoading] = useState(false);

  const isOwner = item?.user_id === user?.id;

  useEffect(() => {
    fetchItem();
  }, [type, id]);

  const fetchItem = async () => {
    setLoading(true);
    try {
      const service = type === 'lost' ? lostItemsService : foundItemsService;
      const response = await service.getById(id);
      setItem(response.data);

      // Fetch potential matches
      if (response.data.status === 'active') {
        try {
          const matchResponse = await searchService.getMatches(id, { limit: 5 });
          setMatches(matchResponse.data.matches || []);
        } catch (e) {
          console.log('No matches found');
        }
      }
    } catch (err) {
      setError('Item not found');
    } finally {
      setLoading(false);
    }
  };

  const handleClaim = async () => {
    if (!claimMessage.trim()) return;

    setClaimLoading(true);
    try {
      // Find a matching item to claim against
      if (matches.length > 0) {
        const matchingItem = matches[0];
        await claimsService.create({
          lost_item_id: type === 'lost' ? id : matchingItem.id,
          found_item_id: type === 'found' ? id : matchingItem.id,
          message: claimMessage,
        });
        setShowClaimModal(false);
        alert('Claim submitted successfully!');
      }
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to submit claim');
    } finally {
      setClaimLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!confirm('Are you sure you want to delete this item?')) return;

    try {
      const service = type === 'lost' ? lostItemsService : foundItemsService;
      await service.delete(id);
      navigate(type === 'lost' ? '/lost-items' : '/found-items');
    } catch (err) {
      alert('Failed to delete item');
    }
  };

  const handleMarkReturned = async () => {
    try {
      await lostItemsService.markReturned(id);
      fetchItem();
    } catch (err) {
      alert('Failed to mark item as returned');
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      weekday: 'long',
      month: 'long',
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

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-8 h-8 animate-spin text-primary-600" />
      </div>
    );
  }

  if (error || !item) {
    return (
      <div className="text-center py-12">
        <AlertCircle className="w-16 h-16 mx-auto mb-4 text-red-400" />
        <h2 className="text-xl font-semibold text-gray-900 mb-2">Item Not Found</h2>
        <p className="text-gray-500 mb-4">{error}</p>
        <button onClick={() => navigate(-1)} className="btn-primary">
          Go Back
        </button>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <button
            onClick={() => navigate(-1)}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <ArrowLeft className="w-5 h-5" />
          </button>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-2xl font-bold text-gray-900">{item.title}</h1>
              <span className={`px-3 py-1 rounded-full text-sm font-medium ${statusColors[item.status]}`}>
                {item.status}
              </span>
            </div>
            <p className="text-gray-600 capitalize">{item.category}</p>
          </div>
        </div>

        {isOwner && (
          <div className="flex gap-2">
            {item.status === 'active' && (
              <button onClick={handleMarkReturned} className="btn-secondary">
                Mark Returned
              </button>
            )}
            <button onClick={handleDelete} className="btn-danger">
              Delete
            </button>
          </div>
        )}
      </div>

      {/* Main Content */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Images */}
        <div className="space-y-4">
          <div className="aspect-video bg-gray-100 rounded-xl overflow-hidden">
            {item.images && item.images.length > 0 ? (
              <img
                src={getImageUrl(item.images[0])}
                alt={item.title}
                className="w-full h-full object-contain"
              />
            ) : (
              <div className="w-full h-full flex items-center justify-center">
                <ImageIcon className="w-20 h-20 text-gray-300" />
              </div>
            )}
          </div>

          {item.images && item.images.length > 1 && (
            <div className="grid grid-cols-4 gap-2">
              {item.images.map((img, idx) => (
                <img
                  key={idx}
                  src={getImageUrl(img)}
                  alt={`${item.title} ${idx + 1}`}
                  className="aspect-square object-cover rounded-lg cursor-pointer"
                />
              ))}
            </div>
          )}
        </div>

        {/* Details */}
        <div className="space-y-6">
          <div className="card">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Details</h2>
            <div className="space-y-3">
              <div>
                <label className="text-sm text-gray-500">Description</label>
                <p className="text-gray-900">{item.description}</p>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm text-gray-500 flex items-center gap-1">
                    <Calendar className="w-4 h-4" />
                    Date
                  </label>
                  <p className="text-gray-900">{formatDate(item.date)}</p>
                </div>

                {item.color && (
                  <div>
                    <label className="text-sm text-gray-500">Color</label>
                    <p className="text-gray-900">{item.color}</p>
                  </div>
                )}

                {item.brand && (
                  <div>
                    <label className="text-sm text-gray-500">Brand</label>
                    <p className="text-gray-900">{item.brand}</p>
                  </div>
                )}
              </div>

              {item.distinguishing_features && (
                <div>
                  <label className="text-sm text-gray-500">Distinguishing Features</label>
                  <p className="text-gray-900">{item.distinguishing_features}</p>
                </div>
              )}
            </div>
          </div>

          <div className="card">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Location</h2>
            {item.location?.address ? (
              <div className="flex items-start gap-2">
                <MapPin className="w-5 h-5 text-gray-400 mt-0.5" />
                <p className="text-gray-900">{item.location.address}</p>
              </div>
            ) : (
              <p className="text-gray-500">Location not specified</p>
            )}

            {item.current_location && (
              <div className="mt-4 pt-4 border-t border-gray-100">
                <label className="text-sm text-gray-500">Current Location</label>
                <p className="text-gray-900">{item.current_location}</p>
              </div>
            )}
          </div>

          <div className="card">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-gray-900">Statistics</h2>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="text-center p-4 bg-gray-50 rounded-lg">
                <Eye className="w-6 h-6 text-gray-400 mx-auto mb-2" />
                <p className="text-2xl font-bold text-gray-900">{item.views}</p>
                <p className="text-sm text-gray-500">Views</p>
              </div>
              <div className="text-center p-4 bg-gray-50 rounded-lg">
                {type === 'lost' ? (
                  <PackageSearch className="w-6 h-6 text-gray-400 mx-auto mb-2" />
                ) : (
                  <PackagePlus className="w-6 h-6 text-gray-400 mx-auto mb-2" />
                )}
                <p className="text-2xl font-bold text-gray-900">{item.match_count}</p>
                <p className="text-sm text-gray-500">Potential Matches</p>
              </div>
            </div>
          </div>

          {/* Actions */}
          {!isOwner && item.status === 'active' && (
            <button
              onClick={() => setShowClaimModal(true)}
              className="btn-primary w-full flex items-center justify-center gap-2"
            >
              <MessageSquare className="w-5 h-5" />
              Claim This Item
            </button>
          )}
        </div>
      </div>

      {/* Potential Matches */}
      {matches.length > 0 && (
        <div className="card">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">
            Potential Matches ({matches.length})
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {matches.map((match, idx) => (
              <Link
                key={`${match.id}-${idx}`}
                to={`/items/${type === 'lost' ? 'found' : 'lost'}/${match.id}`}
                className="p-4 border border-gray-200 rounded-lg hover:border-primary-300 hover:bg-primary-50 transition-colors"
              >
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm text-gray-500 capitalize">{match.category}</span>
                  <span className="text-sm font-medium text-primary-600">
                    {Math.round(match.similarity_score * 100)}% match
                  </span>
                </div>
                <h4 className="font-medium text-gray-900 line-clamp-1">{match.title}</h4>
                <p className="text-sm text-gray-500 line-clamp-2 mt-1">{match.description}</p>
              </Link>
            ))}
          </div>
        </div>
      )}

      {/* Claim Modal */}
      {showClaimModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl p-6 w-full max-w-md">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Claim Item</h3>
            <p className="text-gray-600 mb-4">
              Explain why this item belongs to you. The finder will review your claim.
            </p>
            <textarea
              className="input-field h-32 resize-none"
              placeholder="Describe unique features, contents, or other proof of ownership..."
              value={claimMessage}
              onChange={(e) => setClaimMessage(e.target.value)}
            />
            <div className="flex gap-3 mt-4">
              <button
                onClick={() => setShowClaimModal(false)}
                className="btn-secondary flex-1"
              >
                Cancel
              </button>
              <button
                onClick={handleClaim}
                disabled={!claimMessage.trim() || claimLoading}
                className="btn-primary flex-1 flex items-center justify-center gap-2 disabled:opacity-50"
              >
                {claimLoading ? <Loader2 className="w-5 h-5 animate-spin" /> : null}
                Submit Claim
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
