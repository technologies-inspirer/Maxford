import storybook from '../../assets/user-dashboard-storybook.png';
import maxford from '../../assets/maxford-dashboard.jpg';
import login from '../../assets/maxford-login.jpg';
import classes from '../../assets/maxford-classes.jpg';
import board from '../../assets/maxford-dashboard-2.jpg';

// Decorative crops of reference pictures. Each shows only artwork; all labels and links stay live HTML.
// assets/maxford-dashboard-2.jpg (1643 x 656) is the dashboard design with the tall welcome card; the first
// design (maxford-dashboard.jpg) and the older storybook picture still give the other pages' artwork.
const pictures = { maxford: [maxford, 1541, 672], storybook: [storybook, 1672, 941], login: [login, 1551, 672], classes: [classes, 1418, 752], board: [board, 1643, 656] };
// a crop's third value, when given, is how it sits in its box (SVG preserveAspectRatio)
const regions = {
  // the dashboard (assets/maxford-dashboard-2.jpg)
  'board-welcome': ['board', '120 206 512 444', 'xMidYMax meet'],
  'board-library': ['board', '1098 90 356 150'],
  'dropbox-2': ['board', '858 298 112 148'],
  'paper-maker-2': ['board', '1186 322 90 126'],
  'resources-app-2': ['board', '916 484 164 168'],
  'school-management-2': ['board', '1416 380 142 120'],
  'board-house': ['board', '1398 506 172 146'],
  welcome: ['maxford', '895 82 528 182'],
  library: ['maxford', '865 284 485 122'],
  dropbox: ['maxford', '328 524 108 108'],
  'paper-maker': ['storybook', '704 715 125 105'],
  'resources-app': ['maxford', '998 508 96 124'],
  'school-management': ['maxford', '1290 548 138 86'],
  landscape: ['storybook', '0 837 1672 104'],
  // the sign-in page design (assets/maxford-login.jpg)
  'login-books': ['login', '222 362 486 250'],
  'login-star': ['login', '1360 50 115 110'],
  'login-butterfly': ['login', '882 126 72 70'],
  'login-butterfly-2': ['login', '1450 540 72 74'],
  'login-cloud': ['login', '832 192 108 50'],
  'login-cloud-2': ['login', '0 540 160 132'],
  // Explore Books (assets/maxford-classes.jpg)
  'classes-mark': ['classes', '45 56 68 59'],
  'classes-top': ['classes', '890 16 246 118'],
  'classes-butterfly-left': ['classes', '0 457 53 58'],
  'classes-butterfly-right': ['classes', '1204 505 59 57'],
  'classes-ground': ['classes', '34 588 1190 118']
};

export function DashboardArtwork({ variant }) {
  const [picture, box, fit] = regions[variant];
  const [href, pictureWidth, pictureHeight] = pictures[picture];
  const [x, y, width, height] = box.split(' ').map(Number);
  // the clip keeps the rest of the picture hidden when the box on screen is a different shape from the crop
  const clip = `dashboard-artwork-clip-${variant}`;
  return <svg className={`dashboard-artwork dashboard-artwork-${variant}`} viewBox={box} width={width} height={height} preserveAspectRatio={fit || (variant === 'landscape' ? 'xMidYMin slice' : 'xMaxYMax meet')} fill="none" aria-hidden="true" focusable="false">
    <clipPath id={clip}><rect x={x} y={y} width={width} height={height} /></clipPath>
    <image href={href} x="0" y="0" width={pictureWidth} height={pictureHeight} clipPath={`url(#${clip})`} />
  </svg>;
}

// Small four-point stars that twinkle over a banner; positions are % of the banner.
export function Sparkles({ spots }) {
  return <span className="mx-sparkles" aria-hidden="true">{spots.map(([x, y, size, delay], i) =>
    <svg key={i} className="mx-sparkle" style={{ left: `${x}%`, top: `${y}%`, width: size, height: size, animationDelay: `${delay}s` }} viewBox="0 0 20 20"><path d="M10 0c1 6 4 9 10 10-6 1-9 4-10 10-1-6-4-9-10-10 6-1 9-4 10-10Z" /></svg>)}</span>;
}
