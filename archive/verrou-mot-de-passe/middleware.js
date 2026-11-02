// Park Row Magazine — le site est verrouillé : identifiant et mot de passe demandés
// par le navigateur (authentification HTTP « Basic »). Les identifiants ne sont pas
// dans le code : ce sont les variables d'environnement Vercel BASIC_AUTH_USER et
// BASIC_AUTH_PASSWORD. Pour déverrouiller le site, supprimer ce fichier et redéployer.
import { next } from '@vercel/functions';

export const config = { matcher: '/:path*' };

export default function middleware(request) {
  const user = process.env.BASIC_AUTH_USER;
  const pass = process.env.BASIC_AUTH_PASSWORD;
  // par sécurité, si les variables manquent, on bloque plutôt que d'ouvrir
  if (!user || !pass) return new Response('Site locked.', { status: 503 });

  const header = request.headers.get('authorization') || '';
  const [scheme, encoded] = header.split(' ');
  if (scheme === 'Basic' && encoded) {
    let decoded = '';
    try { decoded = atob(encoded); } catch (e) { /* en-tête invalide */ }
    const i = decoded.indexOf(':');
    if (i >= 0 && decoded.slice(0, i) === user && decoded.slice(i + 1) === pass) return next();
  }
  return new Response('Authentication required.', {
    status: 401,
    headers: { 'WWW-Authenticate': 'Basic realm="Park Row Magazine", charset="UTF-8"' },
  });
}
