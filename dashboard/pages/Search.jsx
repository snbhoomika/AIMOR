import { useState, useRef } from 'react';
import { Link } from 'react-router-dom';
import { searchService, getImageUrl } from '../services/api';
import {
  Search,
  Upload,
  Image as ImageIcon,
  Camera,
  Loader2,
  X,
  Calendar,
  MapPin,
  CheckCircle,
} from 'lucide-react';

export default function SearchPage() {
  const [searchType, setSearchType] = useState('text');
  const [query, setQuery] = useState('');
  const [category, setCategory] = useState('');
  const [itemType, setItemType] = useState('all');
  const [searchImage, setSearchImage] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const fileInputRef = useRef(null);

  const handleImageUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      setSearchImage(file);
      setPreviewUrl(URL.createObjectURL(file));
    }
  };

  const removeImage = () => {
    setSearchImage(null);
    setPreviewUrl(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleSearch = async () => {
    if (searchType === 'text' && !query.trim()) return;
    if (searchType === 'image' && !searchImage) return;

    setLoading(true);
    setResults(null);

    try {
      let response;
      if (searchType === 'text') {
        response = await searchService.byText({
          query_text: query,
          category: category || undefined,
          item_type: itemType,
          limit: 20,
        });
      } else {
        const formData = new FormData();
        formData.append('image', searchImage);
        formData.append('category', category || '');
        formData.append('item_type', itemType);
        formData.append('limit', '20');
        response = await searchService.byImage(formData);
      }
      setResults(response.data);
    } catch (error) {
      console.error('Search failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Search Items</h1>
        <p className="text-gray-600">Find matching lost and found items</p>
      </div>

      {/* Search Type Toggle */}
      <div className="card">
        <div className="flex gap-2 mb-6">
          <button
            onClick={() => {
              setSearchType('text');
              setResults(null);
            }}
            className={`flex-1 py-3 px-4 rounded-lg font-medium transition-colors ${
              searchType === 'text'
                ? 'bg-primary-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            <Search className="w-5 h-5 mx-auto mb-1" />
            Text Search
          </button>
          <button
            onClick={() => {
              setSearchType('image');
              setResults(null);
            }}
            className={`flex-1 py-3 px-4 rounded-lg font-medium transition-colors ${
              searchType === 'image'
                ? 'bg-primary-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            <Camera className="w-5 h-5 mx-auto mb-1" />
            Image Search
          </button>
        </div>

        {/* Text Search Form */}
        {searchType === 'text' && (
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Description
              </label>
              <textarea
                className="input-field h-32 resize-none"
                placeholder="Describe your item... e.g., Blue backpack with laptop compartment"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
              />
            </div>
          </div>
        )}

        {/* Image Search Form */}
        {searchType === 'image' && (
          <div className="space-y-4">
            {previewUrl ? (
              <div className="relative">
                <img
                  src={previewUrl}
                  alt="Search preview"
                  className="w-full max-h-64 object-contain rounded-lg bg-gray-100"
                />
                <button
                  onClick={removeImage}
                  className="absolute top-2 right-2 p-2 bg-red-500 text-white rounded-full hover:bg-red-600"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            ) : (
              <label className="flex flex-col items-center justify-center w-full h-64 border-2 border-dashed border-gray-300 rounded-lg cursor-pointer hover:border-primary-400 transition-colors">
                <div className="flex flex-col items-center justify-center pt-5 pb-6">
                  <Upload className="w-12 h-12 text-gray-400 mb-3" />
                  <p className="mb-2 text-sm text-gray-500">
                    <span className="font-semibold">Click to upload</span> or drag and drop
                  </p>
                  <p className="text-xs text-gray-500">PNG, JPG or JPEG (MAX. 10MB)</p>
                </div>
                <input
                  ref={fileInputRef}
                  type="file"
                  className="hidden"
                  accept="image/*"
                  onChange={handleImageUpload}
                />
              </label>
            )}
          </div>
        )}

        {/* Filters */}
        <div className="flex flex-col sm:flex-row gap-4 mt-4">
          <select
            className="input-field sm:w-48"
            value={category}
            onChange={(e) => setCategory(e.target.value)}
          >
            <option value="">All Categories</option>
            <option value="bag">Bag</option>
            <option value="wallet">Wallet</option>
            <option value="phone">Phone</option>
            <option value="keys">Keys</option>
            <option value="bottle">Bottle</option>
            <option value="laptop">Laptop</option>
            <option value="id_card">ID Card</option>
            <option value="umbrella">Umbrella</option>
            <option value="watch">Watch</option>
            <option value="earphones">Earphones</option>
            <option value="books">Books</option>
            <option value="others">Others</option>
          </select>

          <select
            className="input-field sm:w-48"
            value={itemType}
            onChange={(e) => setItemType(e.target.value)}
          >
            <option value="all">All Items</option>
            <option value="found">Found Items</option>
            <option value="lost">Lost Items</option>
          </select>

          <button
            onClick={handleSearch}
            disabled={loading || (searchType === 'text' && !query.trim()) || (searchType === 'image' && !searchImage)}
            className="btn-primary flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : (
              <Search className="w-5 h-5" />
            )}
            Search
          </button>
        </div>
      </div>

      {/* Results */}
      {results && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-gray-900">
              Search Results ({results.total_matches})
            </h2>
          </div>

          {results.matches && results.matches.length === 0 ? (
            <div className="card text-center py-12">
              <ImageIcon className="w-16 h-16 mx-auto mb-4 text-gray-300" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No matches found</h3>
              <p className="text-gray-500">Try a different search term or image</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {results.matches?.map((item, index) => (
                <Link
                  key={`${item.collection || 'item'}-${item.id}-${index}`}
                  to={`/items/${item.collection || item.match_type === 'image' ? 'found' : 'found'}/${item.id}`}
                  className="card hover:shadow-lg transition-shadow relative"
                >
                  {/* Similarity Score */}
                  {item.similarity_score && (
                    <div className="absolute top-2 right-2 bg-primary-600 text-white px-2 py-1 rounded-full text-xs font-medium">
                      {Math.round(item.similarity_score * 100)}% match
                    </div>
                  )}

                  <div className="aspect-video bg-gray-100 rounded-lg mb-4 overflow-hidden">
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
                  </div>

                  <div className="space-y-2">
                    <h3 className="font-semibold text-gray-900 line-clamp-1">{item.title}</h3>
                    <p className="text-sm text-gray-600 line-clamp-2">{item.description}</p>

                    <div className="flex items-center gap-4 text-sm text-gray-500">
                      <span className="capitalize px-2 py-1 bg-gray-100 rounded">{item.category}</span>
                      <span className="flex items-center gap-1">
                        <ImageIcon className="w-4 h-4" />
                        {item.match_type === 'image' ? 'Image match' : 'Text match'}
                      </span>
                    </div>
                  </div>
                </Link>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
