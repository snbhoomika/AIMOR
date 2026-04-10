import { useState, useEffect } from 'react';
import { claimsService } from '../services/api';
import {
  FileText,
  Check,
  X,
  Clock,
  CheckCircle,
  XCircle,
  Loader2,
  MessageSquare,
} from 'lucide-react';

export default function Claims() {
  const [activeTab, setActiveTab] = useState('my-claims');
  const [myClaims, setMyClaims] = useState([]);
  const [incomingClaims, setIncomingClaims] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchClaims();
  }, []);

  const fetchClaims = async () => {
    setLoading(true);
    try {
      const [myRes, incomingRes] = await Promise.all([
        claimsService.getMyClaims(),
        claimsService.getIncoming(),
      ]);
      setMyClaims(myRes.data);
      setIncomingClaims(incomingRes.data);
    } catch (error) {
      console.error('Failed to fetch claims:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAccept = async (claimId) => {
    try {
      await claimsService.accept(claimId, {});
      fetchClaims();
    } catch (error) {
      console.error('Failed to accept claim:', error);
    }
  };

  const handleReject = async (claimId) => {
    try {
      await claimsService.reject(claimId, { response_message: 'Claim rejected' });
      fetchClaims();
    } catch (error) {
      console.error('Failed to reject claim:', error);
    }
  };

  const handleComplete = async (claimId) => {
    try {
      await claimsService.complete(claimId);
      fetchClaims();
    } catch (error) {
      console.error('Failed to complete claim:', error);
    }
  };

  const statusConfig = {
    pending: { color: 'bg-yellow-100 text-yellow-700', icon: Clock },
    accepted: { color: 'bg-green-100 text-green-700', icon: CheckCircle },
    rejected: { color: 'bg-red-100 text-red-700', icon: XCircle },
    completed: { color: 'bg-purple-100 text-purple-700', icon: Check },
    cancelled: { color: 'bg-gray-100 text-gray-700', icon: X },
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
        <h1 className="text-2xl font-bold text-gray-900">Claims Management</h1>
        <p className="text-gray-600">Track and manage item claims</p>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex gap-6">
          <button
            onClick={() => setActiveTab('my-claims')}
            className={`py-3 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'my-claims'
                ? 'border-primary-600 text-primary-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            My Claims ({myClaims.length})
          </button>
          <button
            onClick={() => setActiveTab('incoming')}
            className={`py-3 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'incoming'
                ? 'border-primary-600 text-primary-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Incoming Claims ({incomingClaims.length})
          </button>
        </nav>
      </div>

      {/* Content */}
      {loading ? (
        <div className="flex items-center justify-center h-64">
          <Loader2 className="w-8 h-8 animate-spin text-primary-600" />
        </div>
      ) : (
        <>
          {activeTab === 'my-claims' && (
            <div className="space-y-4">
              {myClaims.length === 0 ? (
                <div className="card text-center py-12">
                  <FileText className="w-16 h-16 mx-auto mb-4 text-gray-300" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">No claims yet</h3>
                  <p className="text-gray-500">Claims you make on found items will appear here</p>
                </div>
              ) : (
                myClaims.map((claim) => {
                  const config = statusConfig[claim.status];
                  return (
                    <div key={claim.id} className="card">
                      <div className="flex items-start justify-between mb-4">
                        <div>
                          <h3 className="font-semibold text-gray-900">
                            Claim on Lost Item #{claim.lost_item_id.slice(-6)}
                          </h3>
                          <p className="text-sm text-gray-500">
                            Matching Found Item #{claim.found_item_id.slice(-6)}
                          </p>
                        </div>
                        <span className={`px-3 py-1 rounded-full text-sm font-medium flex items-center gap-1 ${config.color}`}>
                          <config.icon className="w-4 h-4" />
                          {claim.status}
                        </span>
                      </div>

                      <div className="space-y-3">
                        <div>
                          <label className="text-sm font-medium text-gray-700">Message</label>
                          <p className="text-gray-600">{claim.message}</p>
                        </div>

                        {claim.response_message && (
                          <div>
                            <label className="text-sm font-medium text-gray-700">Response</label>
                            <p className="text-gray-600">{claim.response_message}</p>
                          </div>
                        )}

                        <div className="flex items-center justify-between pt-3 border-t border-gray-100">
                          <span className="text-sm text-gray-500">
                            Created: {formatDate(claim.created_at)}
                          </span>

                          {claim.status === 'accepted' && (
                            <button
                              onClick={() => handleComplete(claim.id)}
                              className="btn-primary flex items-center gap-2"
                            >
                              <CheckCircle className="w-4 h-4" />
                              Mark as Returned
                            </button>
                          )}
                        </div>
                      </div>
                    </div>
                  );
                })
              )}
            </div>
          )}

          {activeTab === 'incoming' && (
            <div className="space-y-4">
              {incomingClaims.length === 0 ? (
                <div className="card text-center py-12">
                  <FileText className="w-16 h-16 mx-auto mb-4 text-gray-300" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">No incoming claims</h3>
                  <p className="text-gray-500">Claims from people who lost items will appear here</p>
                </div>
              ) : (
                incomingClaims.map((claim) => {
                  const config = statusConfig[claim.status];
                  return (
                    <div key={claim.id} className="card">
                      <div className="flex items-start justify-between mb-4">
                        <div>
                          <h3 className="font-semibold text-gray-900">
                            Claim for Found Item #{claim.found_item_id.slice(-6)}
                          </h3>
                          <p className="text-sm text-gray-500">
                            From Lost Item #{claim.lost_item_id.slice(-6)}
                          </p>
                        </div>
                        <span className={`px-3 py-1 rounded-full text-sm font-medium flex items-center gap-1 ${config.color}`}>
                          <config.icon className="w-4 h-4" />
                          {claim.status}
                        </span>
                      </div>

                      <div className="space-y-3">
                        <div>
                          <label className="text-sm font-medium text-gray-700 flex items-center gap-1">
                            <MessageSquare className="w-4 h-4" />
                            Message
                          </label>
                          <p className="text-gray-600">{claim.message}</p>
                        </div>

                        {claim.verification_questions && claim.verification_questions.length > 0 && (
                          <div>
                            <label className="text-sm font-medium text-gray-700">
                              Verification Questions
                            </label>
                            <div className="mt-2 space-y-2">
                              {claim.verification_questions.map((q, idx) => (
                                <div key={idx} className="bg-gray-50 p-3 rounded-lg">
                                  <p className="text-sm font-medium text-gray-700">Q: {q.question}</p>
                                  <p className="text-sm text-gray-600">A: {q.answer}</p>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}

                        {claim.response_message && (
                          <div>
                            <label className="text-sm font-medium text-gray-700">Your Response</label>
                            <p className="text-gray-600">{claim.response_message}</p>
                          </div>
                        )}

                        <div className="flex items-center justify-between pt-3 border-t border-gray-100">
                          <span className="text-sm text-gray-500">
                            Created: {formatDate(claim.created_at)}
                          </span>

                          {claim.status === 'pending' && (
                            <div className="flex gap-2">
                              <button
                                onClick={() => handleReject(claim.id)}
                                className="btn-danger flex items-center gap-2"
                              >
                                <XCircle className="w-4 h-4" />
                                Reject
                              </button>
                              <button
                                onClick={() => handleAccept(claim.id)}
                                className="btn-primary flex items-center gap-2"
                              >
                                <CheckCircle className="w-4 h-4" />
                                Accept
                              </button>
                            </div>
                          )}

                          {claim.status === 'accepted' && (
                            <button
                              onClick={() => handleComplete(claim.id)}
                              className="btn-primary flex items-center gap-2"
                            >
                              <Check className="w-4 h-4" />
                              Complete Return
                            </button>
                          )}
                        </div>
                      </div>
                    </div>
                  );
                })
              )}
            </div>
          )}
        </>
      )}
    </div>
  );
}
