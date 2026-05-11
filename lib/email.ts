import nodemailer from 'nodemailer';
import sql from './db';

const transporter = nodemailer.createTransport({
  host: process.env.BREVO_SMTP_HOST,
  port: Number(process.env.BREVO_SMTP_PORT),
  secure: false,
  auth: {
    user: process.env.BREVO_SMTP_USER,
    pass: process.env.BREVO_SMTP_KEY,
  },
});

async function getAllUserEmails(): Promise<string[]> {
  const users = await sql`SELECT email FROM users`;
  return users.map((u) => (u as { email: string }).email);
}

export async function sendDeleteAlert(deletedReviews: {
  reviewer_name: string;
  rating: number;
  review_text: string;
}[], onlineCount: number, deletedCount: number, platform: string = 'google') {
  const platformLabel = platform === 'trustpilot' ? 'Trustpilot' : 'Google';
  const recipients = await getAllUserEmails();
  if (recipients.length === 0) return;

  const today = new Date().toLocaleDateString('tr-TR', {
    day: '2-digit', month: 'long', year: 'numeric'
  });

  const tableRows = deletedReviews.map(r => `
    <tr>
      <td style="padding:8px 12px;border-bottom:1px solid #f0f0f0;">${r.reviewer_name || 'Anonim'}</td>
      <td style="padding:8px 12px;border-bottom:1px solid #f0f0f0;text-align:center;">
        ${'★'.repeat(r.rating)}${'☆'.repeat(5 - r.rating)}
      </td>
      <td style="padding:8px 12px;border-bottom:1px solid #f0f0f0;color:#555;">
        ${(r.review_text || '').slice(0, 120)}${(r.review_text || '').length > 120 ? '...' : ''}
      </td>
    </tr>
  `).join('');

  const html = `
    <!DOCTYPE html>
    <html>
    <head><meta charset="utf-8"></head>
    <body style="font-family:Arial,sans-serif;max-width:700px;margin:0 auto;padding:20px;background:#f9f9f9;">
      <div style="background:#fff;border-radius:8px;padding:30px;box-shadow:0 2px 8px rgba(0,0,0,0.08);">
        <div style="border-left:4px solid #ef4444;padding-left:16px;margin-bottom:24px;">
          <h2 style="color:#ef4444;margin:0 0 4px 0;">⚠️ ${platformLabel} Yorumu Silindi Uyarısı</h2>
          <p style="color:#666;margin:0;">Esvita Clinic — ${today}</p>
        </div>

        <p style="font-size:16px;color:#333;">
          Bugün Google Haritalar üzerinde <strong style="color:#ef4444;">${deletedReviews.length} yorum</strong> kaldırılmış görünüyor.
        </p>

        <h3 style="color:#333;border-bottom:2px solid #f0f0f0;padding-bottom:8px;">Silinen Yorumlar</h3>
        <table style="width:100%;border-collapse:collapse;font-size:14px;">
          <thead>
            <tr style="background:#f8f8f8;">
              <th style="padding:10px 12px;text-align:left;color:#666;font-weight:600;">İsim</th>
              <th style="padding:10px 12px;text-align:center;color:#666;font-weight:600;">Puan</th>
              <th style="padding:10px 12px;text-align:left;color:#666;font-weight:600;">Yorum</th>
            </tr>
          </thead>
          <tbody>${tableRows}</tbody>
        </table>

        <div style="background:#f8f8f8;border-radius:6px;padding:16px;margin-top:24px;display:flex;gap:24px;">
          <div style="flex:1;text-align:center;">
            <div style="font-size:28px;font-weight:700;color:#22c55e;">${onlineCount}</div>
            <div style="color:#666;font-size:13px;">Aktif Yorum</div>
          </div>
          <div style="flex:1;text-align:center;">
            <div style="font-size:28px;font-weight:700;color:#ef4444;">${deletedCount}</div>
            <div style="color:#666;font-size:13px;">Silinen Yorum</div>
          </div>
        </div>
      </div>
    </body>
    </html>
  `;

  await transporter.sendMail({
    from: `"${process.env.BREVO_FROM_NAME}" <${process.env.BREVO_FROM_EMAIL}>`,
    to: recipients.join(','),
    subject: `⚠️ Esvita Clinic — ${platformLabel}: ${deletedReviews.length} yorum silindi`,
    html,
  });
}

type ReviewRow = { reviewer_name: string; rating: number; review_text: string };

function stars(n: number) {
  return '★'.repeat(n) + '☆'.repeat(5 - n);
}

function reviewTable(rows: ReviewRow[], emptyMsg: string): string {
  if (rows.length === 0) return `<p style="color:#888;font-size:13px;margin:8px 0;">${emptyMsg}</p>`;
  return `
    <table style="width:100%;border-collapse:collapse;font-size:13px;margin-top:8px;">
      <thead>
        <tr style="background:#f5f5f5;">
          <th style="padding:7px 10px;text-align:left;color:#555;font-weight:600;width:30%;">İsim</th>
          <th style="padding:7px 10px;text-align:center;color:#555;font-weight:600;width:12%;">Puan</th>
          <th style="padding:7px 10px;text-align:left;color:#555;font-weight:600;">Yorum</th>
        </tr>
      </thead>
      <tbody>
        ${rows.map(r => `
          <tr style="border-bottom:1px solid #f0f0f0;">
            <td style="padding:7px 10px;font-weight:500;">${r.reviewer_name || 'Anonim'}</td>
            <td style="padding:7px 10px;text-align:center;color:#f59e0b;">${stars(r.rating)}</td>
            <td style="padding:7px 10px;color:#444;">${(r.review_text || '').slice(0, 120)}${(r.review_text || '').length > 120 ? '…' : ''}</td>
          </tr>
        `).join('')}
      </tbody>
    </table>
  `;
}

function platformSection(
  label: string,
  color: string,
  icon: string,
  data: { newReviews: ReviewRow[]; deletedReviews: ReviewRow[]; totalBefore: number; totalAfter: number }
): string {
  const net = data.totalAfter - data.totalBefore;
  const netColor = net >= 0 ? '#22c55e' : '#ef4444';
  const netSign = net >= 0 ? '+' : '';
  return `
    <div style="border:1px solid #e5e5e5;border-radius:8px;padding:20px;margin-bottom:20px;">
      <h3 style="color:${color};margin:0 0 16px 0;font-size:15px;">
        ${icon} ${label}
      </h3>

      <table style="width:100%;font-size:13px;margin-bottom:16px;">
        <tr>
          <td style="color:#666;padding:4px 0;">Hafta başı toplam</td>
          <td style="text-align:right;font-weight:600;">${data.totalBefore}</td>
        </tr>
        <tr>
          <td style="color:#666;padding:4px 0;">Hafta sonu toplam</td>
          <td style="text-align:right;font-weight:600;">${data.totalAfter}</td>
        </tr>
        <tr>
          <td style="color:#666;padding:4px 0;">Net değişim</td>
          <td style="text-align:right;font-weight:700;color:${netColor};">${netSign}${net}</td>
        </tr>
      </table>

      <div style="margin-bottom:14px;">
        <p style="font-weight:700;color:#333;margin:0 0 6px 0;font-size:13px;">
          ✅ Bu hafta gelen yorumlar (${data.newReviews.length})
        </p>
        ${reviewTable(data.newReviews, 'Bu hafta yeni yorum yok.')}
      </div>

      ${data.deletedReviews.length > 0 ? `
      <div>
        <p style="font-weight:700;color:#ef4444;margin:0 0 6px 0;font-size:13px;">
          ⚠️ Bu hafta silinen yorumlar (${data.deletedReviews.length})
        </p>
        ${reviewTable(data.deletedReviews, '')}
      </div>
      ` : ''}
    </div>
  `;
}

export async function sendWeeklySummary(stats: {
  weekStart: string;
  weekEnd: string;
  google: { newReviews: ReviewRow[]; deletedReviews: ReviewRow[]; totalBefore: number; totalAfter: number };
  trustpilot: { newReviews: ReviewRow[]; deletedReviews: ReviewRow[]; totalBefore: number; totalAfter: number };
}) {
  const recipients = await getAllUserEmails();
  if (recipients.length === 0) return;

  const totalNew = stats.google.newReviews.length + stats.trustpilot.newReviews.length;
  const totalDeleted = stats.google.deletedReviews.length + stats.trustpilot.deletedReviews.length;

  const html = `
    <!DOCTYPE html>
    <html>
    <head><meta charset="utf-8"></head>
    <body style="font-family:Arial,sans-serif;max-width:680px;margin:0 auto;padding:20px;background:#f9f9f9;">
      <div style="background:#fff;border-radius:8px;padding:30px;box-shadow:0 2px 8px rgba(0,0,0,0.08);">
        <div style="border-left:4px solid #3b82f6;padding-left:16px;margin-bottom:24px;">
          <h2 style="color:#3b82f6;margin:0 0 4px 0;">📊 Haftalık Yorum Özeti</h2>
          <p style="color:#666;margin:0;">Esvita Clinic — ${stats.weekStart} – ${stats.weekEnd}</p>
        </div>

        <div style="display:table;width:100%;margin-bottom:24px;">
          <div style="display:table-cell;width:50%;padding-right:8px;">
            <div style="background:#f0fdf4;border-radius:6px;padding:14px;text-align:center;">
              <div style="font-size:28px;font-weight:700;color:#22c55e;">+${totalNew}</div>
              <div style="color:#555;font-size:13px;">Toplam Yeni Yorum</div>
            </div>
          </div>
          <div style="display:table-cell;width:50%;padding-left:8px;">
            <div style="${totalDeleted > 0 ? 'background:#fef2f2' : 'background:#f8f8f8'};border-radius:6px;padding:14px;text-align:center;">
              <div style="font-size:28px;font-weight:700;color:${totalDeleted > 0 ? '#ef4444' : '#999'};">-${totalDeleted}</div>
              <div style="color:#555;font-size:13px;">Toplam Silinen Yorum</div>
            </div>
          </div>
        </div>

        ${platformSection('Google My Business Reviews', '#4285f4', 'G', stats.google)}
        ${platformSection('Trustpilot Reviews', '#00b67a', '★', stats.trustpilot)}

        <p style="color:#999;font-size:11px;text-align:center;margin-top:16px;">
          Bu e-posta Esvita Review Monitor tarafından otomatik olarak gönderilmiştir.
        </p>
      </div>
    </body>
    </html>
  `;

  await transporter.sendMail({
    from: `"${process.env.BREVO_FROM_NAME}" <${process.env.BREVO_FROM_EMAIL}>`,
    to: recipients.join(','),
    subject: `📊 Esvita Clinic — Haftalık Yorum Özeti (${stats.weekStart} – ${stats.weekEnd})`,
    html,
  });
}
