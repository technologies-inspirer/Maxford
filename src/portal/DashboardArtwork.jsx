import storybook from '../../assets/user-dashboard-storybook.png';
import maxford from '../../assets/maxford-dashboard.jpg';

// Decorative crops of two reference pictures. Each shows only artwork; all labels and links stay live HTML.
// assets/maxford-dashboard.jpg (1541 x 672) is the Maxford dashboard design; the older storybook picture
// still gives the landscape along the bottom and the Paper Maker notebook.
const pictures = { maxford: [maxford, 1541, 672], storybook: [storybook, 1672, 941] };
const regions = {
  welcome: ['maxford', '895 82 528 182'],
  library: ['maxford', '865 284 485 122'],
  dropbox: ['maxford', '328 524 108 108'],
  'paper-maker': ['storybook', '704 715 125 105'],
  'resources-app': ['maxford', '998 508 96 124'],
  'school-management': ['maxford', '1290 548 138 86'],
  landscape: ['storybook', '0 837 1672 104']
};

export function DashboardArtwork({ variant }) {
  const [picture, box] = regions[variant];
  const [href, pictureWidth, pictureHeight] = pictures[picture];
  const [x, y, width, height] = box.split(' ').map(Number);
  // the clip keeps the rest of the picture hidden when the box on screen is a different shape from the crop
  const clip = `dashboard-artwork-clip-${variant}`;
  return <svg className={`dashboard-artwork dashboard-artwork-${variant}`} viewBox={box} width={width} height={height} preserveAspectRatio={variant === 'landscape' ? 'xMidYMin slice' : 'xMaxYMax meet'} fill="none" aria-hidden="true" focusable="false">
    <clipPath id={clip}><rect x={x} y={y} width={width} height={height} /></clipPath>
    <image href={href} x="0" y="0" width={pictureWidth} height={pictureHeight} clipPath={`url(#${clip})`} />
  </svg>;
}

// Small four-point stars that twinkle over a banner; positions are % of the banner.
export function Sparkles({ spots }) {
  return <span className="mx-sparkles" aria-hidden="true">{spots.map(([x, y, size, delay], i) =>
    <svg key={i} className="mx-sparkle" style={{ left: `${x}%`, top: `${y}%`, width: size, height: size, animationDelay: `${delay}s` }} viewBox="0 0 20 20"><path d="M10 0c1 6 4 9 10 10-6 1-9 4-10 10-1-6-4-9-10-10 6-1 9-4 10-10Z" /></svg>)}</span>;
}
