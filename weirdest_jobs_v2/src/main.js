'use strict';
window.boot = async () => { for (const f of ['Luckiest', 'CinzelD', 'Cinzel', 'Slab', 'Bree']) await document.fonts.load(`40px ${f}`); buildTextures(); if (window.buildEnv) buildEnv(); return document.fonts.check('40px Slab'); };
window.renderAt = t => { if (window.drawFilm) drawFilm(t); };
