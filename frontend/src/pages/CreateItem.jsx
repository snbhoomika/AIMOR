import { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { lostItemsService, foundItemsService } from '../services/api';
import { ArrowLeft, Upload, X, Loader2, MapPin, AlertCircle } from 'lucide-react';

export default function CreateItem({ type }) {
  const navigate = useNavigate();
  const fileInputRef = useRef(null);
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    category: '',
    color: '',
    brand: '',
    distinguishing_features: '',
    date: new Date().toISOString().split('T')[0],
    location: '',
    current_location: type === 'found' ? '' : undefined,
  });
  const [images, setImages] = useState([]);
  const [previewUrls, setPreviewUrls] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const categories = [
    { value: 'bag', label: 'Bag' },
    { value: 'wallet', label: 'Wallet' },
    { value: 'phone', label: 'Phone' },
    { value: 'keys', label: 'Keys' },
    { value: 'bottle', label: 'Bottle' },
    { value: 'laptop', label: 'Laptop' },
    { value: 'id_card', label: 'ID Card' },
    { value: 'umbrella', label: 'Umbrella' },
    { value: 'watch', label: 'Watch' },
    { value: 'earphones', label: 'Earphones' },
    { value: 'books', label: 'Books' },
    { value: 'others', label: 'Others' },
  ];

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };

  const handleImageUpload = (e) => {
    const files = Array.from(e.target.files);
    if (files.length > 5) {
      setError('Maximum 5 images allowed');
      return;
    }

    const newPreviewUrls = files.map((file) => URL.createObjectURL(file));
    setImages([...images, ...files]);
    setPreviewUrls([...previewUrls, ...newPreviewUrls]);
  };

  const removeImage = (index) => {
    const newImages = images.filter((_, i) => i !== index);
    const newPreviews = previewUrls.filter((_, i) => i !== index);
    setImages(newImages);
    setPreviewUrls(newPreviews);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const data = new FormData();
      data.append('title', formData.title);
      data.append('description', formData.description);
      data.append('category', formData.category);
      data.append('date', formData.date);
      data.append('color', formData.color || '');
      data.append('brand', formData.brand || '');
      data.append('distinguishing_features', formData.distinguishing_features || '');
      data.append('location', formData.location || '');

      if (type === 'found' && formData.current_location) {
        data.append('current_location', formData.current_location);
      }

      images.forEach((image) => {
        data.append('images', image);
      });

      const service = type === 'lost' ? lostItemsService : foundItemsService;
      await service.create(data);

      navigate(type === 'lost' ? '/lost-items' : '/found-items');
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to create item');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center gap-4">
        <button
          onClick={() => navigate(-1)}
          className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
        >
          <ArrowLeft className="w-5 h-5" />
        </button>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">
            Report {type === 'lost' ? 'Lost' : 'Found'} Item
          </h1>
          <p className="text-gray-600">
            {type === 'lost'
              ? 'Help others know what you lost so they can help you find it'
              : 'Help someone find their item by providing details'}
          </p>
        </div>
      </div>

      {/* Error */}
      {error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg flex items-center gap-2 text-red-700">
          <AlertCircle className="w-5 h-5" />
          {error}
        </div>
      )}

      {/* Form */}
      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="card">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Basic Information</h2>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Title *
              </label>
              <input
                type="text"
                name="title"
                required
                className="input-field"
                placeholder={type === 'lost' ? 'e.g., Blue Laptop Bag' : 'e.g., Black Wallet Found'}
                value={formData.title}
                onChange={handleInputChange}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Description *
              </label>
              <textarea
                name="description"
                required
                className="input-field h-32 resize-none"
                placeholder="Describe the item in detail..."
                value={formData.description}
                onChange={handleInputChange}
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Category *
                </label>
                <select
                  name="category"
                  required
                  className="input-field"
                  value={formData.category}
                  onChange={handleInputChange}
                >
                  <option value="">Select category</option>
                  {categories.map((cat) => (
                    <option key={cat.value} value={cat.value}>
                      {cat.label}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Date *
                </label>
                <input
                  type="date"
                  name="date"
                  required
                  className="input-field"
                  value={formData.date}
                  onChange={handleInputChange}
                  max={new Date().toISOString().split('T')[0]}
                />
              </div>
            </div>
          </div>
        </div>

        <div className="card">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Additional Details</h2>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Color
              </label>
              <input
                type="text"
                name="color"
                className="input-field"
                placeholder="e.g., Blue, Black"
                value={formData.color}
                onChange={handleInputChange}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Brand
              </label>
              <input
                type="text"
                name="brand"
                className="input-field"
                placeholder="e.g., Apple, Nike"
                value={formData.brand}
                onChange={handleInputChange}
              />
            </div>
          </div>

          <div className="mt-4">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Distinguishing Features
            </label>
            <textarea
              name="distinguishing_features"
              className="input-field h-24 resize-none"
              placeholder="Any unique marks, scratches, stickers, etc."
              value={formData.distinguishing_features}
              onChange={handleInputChange}
            />
          </div>
        </div>

        <div className="card">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">
            <MapPin className="w-5 h-5 inline mr-2" />
            Location
          </h2>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                {type === 'lost' ? 'Where did you lose it?' : 'Where did you find it?'}
              </label>
              <input
                type="text"
                name="location"
                className="input-field"
                placeholder="e.g., Library, 2nd Floor, Near Elevator"
                value={formData.location}
                onChange={handleInputChange}
              />
            </div>

            {type === 'found' && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Current Location (Where you're keeping it)
                </label>
                <input
                  type="text"
                  name="current_location"
                  className="input-field"
                  placeholder="e.g., Security Office, Main Building"
                  value={formData.current_location}
                  onChange={handleInputChange}
                />
              </div>
            )}
          </div>
        </div>

        <div className="card">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">
            <Upload className="w-5 h-5 inline mr-2" />
            Images (Optional)
          </h2>

          <p className="text-sm text-gray-600 mb-4">
            Upload up to 5 images to help identify the item
          </p>

          <div className="grid grid-cols-3 gap-4">
            {previewUrls.map((url, index) => (
              <div key={index} className="relative aspect-square">
                <img
                  src={url}
                  alt={`Preview ${index + 1}`}
                  className="w-full h-full object-cover rounded-lg"
                />
                <button
                  type="button"
                  onClick={() => removeImage(index)}
                  className="absolute -top-2 -right-2 p-1 bg-red-500 text-white rounded-full hover:bg-red-600"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            ))}

            {images.length < 5 && (
              <label className="aspect-square flex flex-col items-center justify-center border-2 border-dashed border-gray-300 rounded-lg cursor-pointer hover:border-primary-400 transition-colors">
                <Upload className="w-8 h-8 text-gray-400 mb-2" />
                <span className="text-sm text-gray-500">Add Image</span>
                <input
                  ref={fileInputRef}
                  type="file"
                  className="hidden"
                  accept="image/*"
                  multiple
                  onChange={handleImageUpload}
                />
              </label>
            )}
          </div>
        </div>

        <div className="flex gap-4">
          <button
            type="button"
            onClick={() => navigate(-1)}
            className="btn-secondary flex-1"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={loading}
            className="btn-primary flex-1 flex items-center justify-center gap-2 disabled:opacity-50"
          >
            {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : null}
            {type === 'lost' ? 'Report Lost Item' : 'Report Found Item'}
          </button>
        </div>
      </form>
    </div>
  );
}
