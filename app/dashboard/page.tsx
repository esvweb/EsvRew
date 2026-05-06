'use client';

import { useEffect, useState } from 'react';

interface Review {
  id: number;
  review_id: string;
  reviewer_name: string;
  rating: number;
  review_text: string;
  first_seen_date: string;
  last_seen_date: string;
  status: 'online' | 'deleted';
  deleted_date: string | null;
}

interface ReviewsResponse {
  reviews: Review[];
  total: number;
  online_count: number;
  deleted_count: number;
  pages: number;
}

function Stars({ rating }: { rating: number }) {
  return (
    <span className="text-yellow-400">
      {'★'.repeat(rating)}
      <span className="text-gray-200">{'★'.repeat(5 - rating)}</span>
    </span>
  );
}

function ExpandableText({ text, max = 120 }: { text: string; max?: number }) {
  const [expanded, setExpanded] = useState(false);
  if (!text) return <span className="text-gray-400 italic">—</span>;
  if (text.length <= max) return <span>{text}</span>;

  return (
    <span>
      {expanded ? text : text.slice(0, max) + '...'}
      <button
        onClick={() => setExpanded(!expanded)}
        className="ml-1 text-blue-500 text-xs underline"
      >
        {expanded ? 'daha az' : 'devamı'}
      </button>
    </span>
  );
}

function formatDate(d: string | null) {
  if (!d) return '—';
  return new Date(d).toLocaleDateString('tr-TR');
}

export default function DashboardPage() {
  const [data, setData] = useState<ReviewsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [status, setStatus] = useState('');
  const [rating, setRating] = useState('');
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(1);
  const [weeklyStats, setWeeklyStats] = useState({ newReviews: 0, deletedReviews: 0 });

  async function fetchReviews() {
    setLoading(true);
    const params = new URLSearchParams();
    if (status) params.set('status', status);
    if (rating) params.set('rating', rating);
    if (search) params.set('search', search);
    params.set('page', String(page));

    const res = await fetch(`/api/reviews?${params}`);
    if (res.ok) {
      const json = await res.json();
      setData(json);
    }
    setLoading(false);
  }

  async function fetchWeeklyStats() {
    const weekStart = new Date();
    weekStart.setDate(weekStart.getDate() - 7);
    const weekStartStr = weekStart.toISOString().split('T')[0];

    const res = await fetch(`/api/reviews?status=&search=&page=1&limit=1000`);
    if (!res.ok) return;
    const json: ReviewsResponse = await res.json();

    const newR = json.reviews.filter(r =>
      r.first_seen_date >= weekStartStr
    ).length;
    const delR = json.reviews.filter(r =>
      r.deleted_date && r.deleted_date >= weekStartStr
    ).length;
    setWeeklyStats({ newReviews: newR, deletedReviews: delR });
  }

  useEffect(() => {
    fetchReviews();
  }, [status, rating, search, page]);

  useEffect(() => {
    fetchWeeklyStats();
  }, []);

  const handleFilterChange = () => {
    setPage(1);
  };

  return (
    <div>
      <div className="mb-8">
        <h2 className="text-2xl font-bold text-gray-900">Dashboard</h2>
        <p className="text-gray-500 text-sm mt-1">Google Yorumları İzleme Paneli</p>
      </div>

      <div className="grid grid-cols-2 gap-4 mb-8 lg:grid-cols-5">
        <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
          <p className="text-xs text-gray-500 uppercase tracking-wide font-medium">Toplam</p>
          <p className="text-3xl font-bold text-gray-900 mt-1">
            {data ? data.online_count + data.deleted_count : '—'}
          </p>
        </div>
        <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
          <p className="text-xs text-green-600 uppercase tracking-wide font-medium">Aktif</p>
          <p className="text-3xl font-bold text-green-600 mt-1">
            {data?.online_count ?? '—'}
          </p>
        </div>
        <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
          <p className="text-xs text-red-500 uppercase tracking-wide font-medium">Silinen</p>
          <p className="text-3xl font-bold text-red-500 mt-1">
            {data?.deleted_count ?? '—'}
          </p>
        </div>
        <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
          <p className="text-xs text-blue-600 uppercase tracking-wide font-medium">Bu Hafta Yeni</p>
          <p className="text-3xl font-bold text-blue-600 mt-1">
            +{weeklyStats.newReviews}
          </p>
        </div>
        <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
          <p className="text-xs text-orange-500 uppercase tracking-wide font-medium">Bu Hafta Silinen</p>
          <p className="text-3xl font-bold text-orange-500 mt-1">
            -{weeklyStats.deletedReviews}
          </p>
        </div>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-gray-100">
        <div className="p-5 border-b border-gray-100 flex flex-wrap gap-3">
          <select
            value={status}
            onChange={e => { setStatus(e.target.value); handleFilterChange(); }}
            className="px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">Tüm Durumlar</option>
            <option value="online">Aktif</option>
            <option value="deleted">Silindi</option>
          </select>

          <select
            value={rating}
            onChange={e => { setRating(e.target.value); handleFilterChange(); }}
            className="px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">Tüm Puanlar</option>
            <option value="5">★★★★★ (5)</option>
            <option value="4">★★★★☆ (4)</option>
            <option value="3">★★★☆☆ (3)</option>
            <option value="2">★★☆☆☆ (2)</option>
            <option value="1">★☆☆☆☆ (1)</option>
          </select>

          <input
            type="text"
            value={search}
            onChange={e => { setSearch(e.target.value); handleFilterChange(); }}
            placeholder="İsim veya yorum ara..."
            className="flex-1 min-w-48 px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-100 bg-gray-50">
                <th className="text-left px-5 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">Puan</th>
                <th className="text-left px-5 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">İsim</th>
                <th className="text-left px-5 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">Yorum</th>
                <th className="text-left px-5 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">Durum</th>
                <th className="text-left px-5 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">İlk Görülme</th>
                <th className="text-left px-5 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">Silinme</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr>
                  <td colSpan={6} className="text-center py-12 text-gray-400">
                    Yükleniyor...
                  </td>
                </tr>
              ) : data?.reviews.length === 0 ? (
                <tr>
                  <td colSpan={6} className="text-center py-12 text-gray-400">
                    Yorum bulunamadı.
                  </td>
                </tr>
              ) : (
                data?.reviews.map(review => (
                  <tr key={review.id} className="border-b border-gray-50 hover:bg-gray-50 transition-colors">
                    <td className="px-5 py-3.5">
                      <Stars rating={review.rating} />
                    </td>
                    <td className="px-5 py-3.5 font-medium text-gray-900 whitespace-nowrap">
                      {review.reviewer_name || 'Anonim'}
                    </td>
                    <td className="px-5 py-3.5 text-gray-600 max-w-xs">
                      <ExpandableText text={review.review_text} />
                    </td>
                    <td className="px-5 py-3.5">
                      {review.status === 'online' ? (
                        <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-700">
                          Aktif
                        </span>
                      ) : (
                        <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-700">
                          Silindi
                        </span>
                      )}
                    </td>
                    <td className="px-5 py-3.5 text-gray-500 whitespace-nowrap">
                      {formatDate(review.first_seen_date)}
                    </td>
                    <td className="px-5 py-3.5 text-gray-500 whitespace-nowrap">
                      {formatDate(review.deleted_date)}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {data && data.pages > 1 && (
          <div className="p-5 border-t border-gray-100 flex items-center justify-between">
            <p className="text-sm text-gray-500">
              Toplam {data.total} yorum — Sayfa {page} / {data.pages}
            </p>
            <div className="flex gap-2">
              <button
                onClick={() => setPage(p => Math.max(1, p - 1))}
                disabled={page === 1}
                className="px-3 py-1.5 text-sm border border-gray-200 rounded-lg hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed"
              >
                Önceki
              </button>
              <button
                onClick={() => setPage(p => Math.min(data.pages, p + 1))}
                disabled={page === data.pages}
                className="px-3 py-1.5 text-sm border border-gray-200 rounded-lg hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed"
              >
                Sonraki
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
