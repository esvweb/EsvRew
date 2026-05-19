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
  modified_date: string | null;
  original_text: string | null;
  original_rating: number | null;
  platform: 'google' | 'trustpilot';
}

interface ReviewsResponse {
  reviews: Review[];
  total: number;
  online_count: number;
  deleted_count: number;
  pages: number;
}

type Platform = 'all' | 'google' | 'trustpilot';
type Period = '30d' | '3m' | '6m' | '1y' | 'custom' | 'all';

function Stars({ rating }: { rating: number }) {
  return (
    <span className="text-yellow-500 text-base">
      {'★'.repeat(rating)}<span className="text-gray-300">{'★'.repeat(5 - rating)}</span>
    </span>
  );
}

function ExpandableText({ text, max = 120 }: { text: string; max?: number }) {
  const [expanded, setExpanded] = useState(false);
  if (!text) return <span className="text-gray-400 italic text-xs">Sadece yıldız</span>;
  if (text.length <= max) return <span className="text-gray-800">{text}</span>;
  return (
    <span className="text-gray-800">
      {expanded ? text : text.slice(0, max) + '...'}
      <button onClick={() => setExpanded(!expanded)} className="ml-1 text-blue-600 text-xs underline font-medium">
        {expanded ? 'daha az' : 'devamı'}
      </button>
    </span>
  );
}

function PlatformBadge({ platform }: { platform: string }) {
  if (platform === 'trustpilot') {
    return <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-semibold bg-green-100 text-green-800">★ Trustpilot</span>;
  }
  return <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-semibold bg-blue-100 text-blue-800">G Google</span>;
}

function formatDate(d: string | null) {
  if (!d) return '—';
  return new Date(d).toLocaleDateString('tr-TR');
}

function getPeriodDates(period: Period, customFrom: string, customTo: string): { from: string; to: string } | null {
  if (period === 'all') return null;
  if (period === 'custom') return customFrom && customTo ? { from: customFrom, to: customTo } : null;
  const to = new Date();
  const from = new Date();
  if (period === '30d') from.setDate(from.getDate() - 30);
  if (period === '3m') from.setMonth(from.getMonth() - 3);
  if (period === '6m') from.setMonth(from.getMonth() - 6);
  if (period === '1y') from.setFullYear(from.getFullYear() - 1);
  return { from: from.toISOString().split('T')[0], to: to.toISOString().split('T')[0] };
}

export default function DashboardPage() {
  const [data, setData] = useState<ReviewsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [platform, setPlatform] = useState<Platform>('all');
  const [status, setStatus] = useState('');
  const [rating, setRating] = useState('');
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(1);
  const [period, setPeriod] = useState<Period>('all');
  const [customFrom, setCustomFrom] = useState('');
  const [customTo, setCustomTo] = useState('');
  const [weeklyStats, setWeeklyStats] = useState<Record<Platform, { newReviews: number; deletedReviews: number }>>({
    all: { newReviews: 0, deletedReviews: 0 },
    google: { newReviews: 0, deletedReviews: 0 },
    trustpilot: { newReviews: 0, deletedReviews: 0 },
  });
  const [expandedOriginal, setExpandedOriginal] = useState<Set<number>>(new Set());

  async function fetchReviews() {
    setLoading(true);
    const params = new URLSearchParams();
    if (platform !== 'all') params.set('platform', platform);
    if (status) params.set('status', status);
    if (rating) params.set('rating', rating);
    if (search) params.set('search', search);
    params.set('page', String(page));

    const dates = getPeriodDates(period, customFrom, customTo);
    if (dates) {
      params.set('date_from', dates.from);
      params.set('date_to', dates.to);
    }

    const res = await fetch(`/api/reviews?${params}`);
    if (res.ok) setData(await res.json());
    setLoading(false);
  }

  async function fetchWeeklyStats() {
    const weekStart = new Date();
    weekStart.setDate(weekStart.getDate() - 7);
    const weekStartStr = weekStart.toISOString().split('T')[0];
    const res = await fetch(`/api/reviews?page=1&limit=2000`);
    if (!res.ok) return;
    const json: ReviewsResponse = await res.json();
    const calc = (p: Platform) => {
      const filtered = p === 'all' ? json.reviews : json.reviews.filter(r => r.platform === p);
      return {
        newReviews: filtered.filter(r => r.first_seen_date >= weekStartStr).length,
        deletedReviews: filtered.filter(r => r.deleted_date && r.deleted_date >= weekStartStr).length,
      };
    };
    setWeeklyStats({ all: calc('all'), google: calc('google'), trustpilot: calc('trustpilot') });
  }

  useEffect(() => { fetchReviews(); }, [platform, status, rating, search, page, period, customFrom, customTo]);
  useEffect(() => { fetchWeeklyStats(); }, []);

  const ws = weeklyStats[platform];

  function toggleOriginal(id: number) {
    setExpandedOriginal(prev => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id); else next.add(id);
      return next;
    });
  }

  return (
    <div>
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-950">Dashboard</h2>
        <p className="text-gray-600 text-sm mt-1 font-medium">Google & Trustpilot Yorum İzleme Paneli</p>
      </div>

      {/* Platform Tabs */}
      <div className="flex gap-2 mb-6">
        {(['all', 'google', 'trustpilot'] as Platform[]).map(p => (
          <button key={p} onClick={() => { setPlatform(p); setPage(1); }}
            className={`px-4 py-2 rounded-lg text-sm font-semibold transition-colors ${
              platform === p
                ? p === 'trustpilot' ? 'bg-green-600 text-white' : p === 'google' ? 'bg-blue-600 text-white' : 'bg-gray-900 text-white'
                : 'bg-white border border-gray-200 text-gray-700 hover:bg-gray-50'
            }`}>
            {p === 'all' ? 'Tümü' : p === 'google' ? 'G  Google' : '★ Trustpilot'}
          </button>
        ))}
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-2 gap-4 mb-8 lg:grid-cols-5">
        {[
          { label: 'Toplam', value: data ? data.online_count + data.deleted_count : '—', color: 'text-gray-950' },
          { label: 'Aktif', value: data?.online_count ?? '—', color: 'text-green-700' },
          { label: 'Silinen', value: data?.deleted_count ?? '—', color: 'text-red-600' },
          { label: 'Bu Hafta Yeni', value: `+${ws.newReviews}`, color: 'text-blue-700' },
          { label: 'Bu Hafta Silinen', value: `-${ws.deletedReviews}`, color: 'text-orange-600' },
        ].map(card => (
          <div key={card.label} className="bg-white rounded-xl p-5 shadow-sm border border-gray-200">
            <p className="text-xs text-gray-600 uppercase tracking-wide font-semibold">{card.label}</p>
            <p className={`text-3xl font-bold mt-1 ${card.color}`}>{String(card.value)}</p>
          </div>
        ))}
      </div>

      {/* Table */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200">
        {/* Filters */}
        <div className="p-5 border-b border-gray-200 space-y-3">
          {/* Period filter row */}
          <div className="flex flex-wrap gap-2 items-center">
            <span className="text-xs font-semibold text-gray-600 uppercase tracking-wide">Dönem:</span>
            {([['all', 'Tümü'], ['30d', 'Son 30 gün'], ['3m', 'Son 3 ay'], ['6m', 'Son 6 ay'], ['1y', 'Son 1 yıl'], ['custom', 'Özel']] as [Period, string][]).map(([val, label]) => (
              <button key={val} onClick={() => { setPeriod(val); setPage(1); }}
                className={`px-3 py-1 rounded-lg text-xs font-semibold transition-colors ${
                  period === val ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}>
                {label}
              </button>
            ))}
            {period === 'custom' && (
              <div className="flex items-center gap-2">
                <input type="date" value={customFrom} onChange={e => { setCustomFrom(e.target.value); setPage(1); }}
                  className="px-2 py-1 border border-gray-300 rounded text-xs" />
                <span className="text-gray-500 text-xs">—</span>
                <input type="date" value={customTo} onChange={e => { setCustomTo(e.target.value); setPage(1); }}
                  className="px-2 py-1 border border-gray-300 rounded text-xs" />
              </div>
            )}
          </div>

          {/* Other filters row */}
          <div className="flex flex-wrap gap-3">
            <select value={status} onChange={e => { setStatus(e.target.value); setPage(1); }}
              className="px-3 py-2 border border-gray-300 rounded-lg text-sm text-gray-800 font-medium focus:outline-none focus:ring-2 focus:ring-blue-500">
              <option value="">Tüm Durumlar</option>
              <option value="online">Aktif</option>
              <option value="deleted">Silindi</option>
            </select>
            <select value={rating} onChange={e => { setRating(e.target.value); setPage(1); }}
              className="px-3 py-2 border border-gray-300 rounded-lg text-sm text-gray-800 font-medium focus:outline-none focus:ring-2 focus:ring-blue-500">
              <option value="">Tüm Puanlar</option>
              <option value="5">★★★★★ (5)</option>
              <option value="4">★★★★☆ (4)</option>
              <option value="3">★★★☆☆ (3)</option>
              <option value="2">★★☆☆☆ (2)</option>
              <option value="1">★☆☆☆☆ (1)</option>
            </select>
            <input type="text" value={search} onChange={e => { setSearch(e.target.value); setPage(1); }}
              placeholder="İsim veya yorum ara..."
              className="flex-1 min-w-48 px-3 py-2 border border-gray-300 rounded-lg text-sm text-gray-800 focus:outline-none focus:ring-2 focus:ring-blue-500" />
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-200 bg-gray-50">
                {['Puan', 'İsim', 'Yorum', 'Platform', 'Durum', 'İlk Görülme', 'Değişiklik', 'Silinme'].map(h => (
                  <th key={h} className="text-left px-4 py-3 text-xs font-bold text-gray-700 uppercase tracking-wide">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr><td colSpan={8} className="text-center py-12 text-gray-500 font-medium">Yükleniyor...</td></tr>
              ) : data?.reviews.length === 0 ? (
                <tr><td colSpan={8} className="text-center py-12 text-gray-500 font-medium">Yorum bulunamadı.</td></tr>
              ) : (
                data?.reviews.map(review => (
                  <>
                    <tr key={review.id} className={`border-b border-gray-100 hover:bg-gray-50 transition-colors ${review.modified_date ? 'bg-amber-50' : ''}`}>
                      <td className="px-4 py-3"><Stars rating={review.rating} /></td>
                      <td className="px-4 py-3 font-semibold text-gray-900 whitespace-nowrap">{review.reviewer_name || 'Anonim'}</td>
                      <td className="px-4 py-3 max-w-xs"><ExpandableText text={review.review_text} /></td>
                      <td className="px-4 py-3"><PlatformBadge platform={review.platform} /></td>
                      <td className="px-4 py-3">
                        {review.status === 'online'
                          ? <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-green-100 text-green-800">Aktif</span>
                          : <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-red-100 text-red-800">Silindi</span>}
                      </td>
                      <td className="px-4 py-3 text-gray-700 font-medium whitespace-nowrap">{formatDate(review.first_seen_date)}</td>
                      <td className="px-4 py-3">
                        {review.modified_date ? (
                          <button onClick={() => toggleOriginal(review.id)}
                            className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-semibold bg-amber-100 text-amber-800 hover:bg-amber-200 transition-colors">
                            ✏️ {formatDate(review.modified_date)}
                          </button>
                        ) : <span className="text-gray-400">—</span>}
                      </td>
                      <td className="px-4 py-3 text-gray-700 font-medium whitespace-nowrap">{formatDate(review.deleted_date)}</td>
                    </tr>
                    {review.modified_date && expandedOriginal.has(review.id) && (
                      <tr key={`${review.id}-orig`} className="bg-amber-50 border-b border-amber-100">
                        <td colSpan={8} className="px-4 py-3">
                          <div className="text-xs text-amber-800 font-semibold mb-1">Orijinal yorum ({formatDate(review.first_seen_date)}):</div>
                          <div className="text-sm text-gray-600">
                            {review.original_rating && review.original_rating !== review.rating && (
                              <span className="text-yellow-500 mr-2">
                                {'★'.repeat(review.original_rating)}{'☆'.repeat(5 - review.original_rating)}
                              </span>
                            )}
                            {review.original_text || '(metin yok)'}
                          </div>
                        </td>
                      </tr>
                    )}
                  </>
                ))
              )}
            </tbody>
          </table>
        </div>

        {data && data.pages > 1 && (
          <div className="p-5 border-t border-gray-200 flex items-center justify-between">
            <p className="text-sm text-gray-700 font-medium">Toplam {data.total} yorum — Sayfa {page} / {data.pages}</p>
            <div className="flex gap-2">
              <button onClick={() => setPage(p => Math.max(1, p - 1))} disabled={page === 1}
                className="px-3 py-1.5 text-sm font-medium border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed text-gray-700">Önceki</button>
              <button onClick={() => setPage(p => Math.min(data.pages, p + 1))} disabled={page === data.pages}
                className="px-3 py-1.5 text-sm font-medium border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed text-gray-700">Sonraki</button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
