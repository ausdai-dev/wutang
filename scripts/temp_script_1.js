

(function() {

  "use strict";



  // 1. 加载内联数据

  var RAW_DATA = JSON.parse(document.getElementById('wutang-data').textContent);

  var CLASSICS = RAW_DATA.classics || [];

  var SCENARIOS = RAW_DATA.scenarios || [];

  var MICRO_ACTIONS = RAW_DATA.microActions || {};

  var BRAND = RAW_DATA.brand || {};

  var RISK_HIGH = RAW_DATA.riskHigh || [];

  var RISK_REVIEW = RAW_DATA.riskReview || [];

  var RISK_PATTERNS = (RAW_DATA.riskPatterns || []).map(function(p) { return new RegExp(p); });

  var SYNTHETIC_CASES = RAW_DATA.syntheticCases || [];

  var ARTICLE_DRAFTS = RAW_DATA.articleDrafts || {};

  var SAGE_AVATARS = RAW_DATA.sageAvatars || {};

  var CARDS_MINDSET = RAW_DATA.cardsMindset || [];

  var CARDS_WISDOM = RAW_DATA.cardsWisdom || [];

  var CARDS_ACTION = RAW_DATA.cardsAction || [];

  var CARDS_MANIFEST = RAW_DATA.cardsManifest || { cards: [], bookmarks: [] };

  var ZEN_ASSETS = RAW_DATA.zenAssets || { cards: {}, bookmarks: {} };

  // PRD 3.0 新增知识与量表语料

  var INSTRUMENTS = RAW_DATA.instruments || [];

  var SCORING_RULES = RAW_DATA.scoringRules || {};

  var INTERPRETATION_COPY = RAW_DATA.interpretationCopy || {};

  var MENTAL_RESOURCES = RAW_DATA.mentalResources || [];

  var THEME_PACKS = RAW_DATA.themePacks || [];

  var PRACTICE_SCENARIOS = RAW_DATA.practiceScenarios || [];

  var ZEN_CARDS_96 = RAW_DATA.zenCards96 || [];



  // 禅意卡牌与书笺静态/离线 Base64 资产解析器

  function getCardAsset(cardId, face) {

    var key = cardId + '_' + face;

    if (ZEN_ASSETS.cards && ZEN_ASSETS.cards[key]) {

      return ZEN_ASSETS.cards[key];

    }

    return 'assets/cards/' + face + '/' + cardId + '_' + face + '.png';

  }



  function getBookmarkAsset(bmId) {

    if (ZEN_ASSETS.bookmarks && ZEN_ASSETS.bookmarks[bmId]) {

      return ZEN_ASSETS.bookmarks[bmId];

    }

    return 'assets/bookmarks/' + bmId + '.png';

  }



  // 先贤印章头像解析器

  function getSageInfo(author, book) {

    var text = (String(author || '') + ' ' + String(book || '')).trim();

    for (var k in SAGE_AVATARS) {

      if (k === 'default') continue;

      var info = SAGE_AVATARS[k];

      var kws = info.keywords || [info.name];

      for (var i = 0; i < kws.length; i++) {

        if (text.indexOf(kws[i]) >= 0) {

          return info;

        }

      }

    }

    return SAGE_AVATARS['default'] || {

      name: '悟堂先贤',

      title: '国学先哲',

      era: '国学传世经典',

      motto: '不说教先接住 · 借古人走眼前',

      color: 'rgb(140, 58, 43)',

      b64: ''

    };

  }



  // 状态中心 (PRD 2.0)

  var appState = {

    mode: 'client', // 'client' | 'studio'

    mainTab: 'relief', // 'relief' | 'mine' | 'studio'

    isManagerLoggedIn: (function() {

      try { return localStorage.getItem('wutang_manager_active') === 'true'; } catch(e) { return false; }

    })(),

    currentUser: (function() {

      try {

        var u = localStorage.getItem('wutang_current_user');

        return u ? JSON.parse(u) : null;

      } catch(e) { return null; }

    })(),

    clientView: 'userHome', // 'userHome' | 'userLoading' | 'userResult' | 'userSafety' | 'userCard'

    entryTab: 'direct', // 'direct' | 'card'

    awarenessIndex: 0,

    awarenessFlipped: false,

    awarenessReaction: null,

    studioView: 'studioOverview', // 'studioOverview' | 'studioCards' | 'studioNewTask' | 'studioPipeline' | 'studioReview' | 'studioClassics'

    selectedScenario: null,

    currentCaseId: null,

    currentResult: null,

    currentCards: { mindset: null, wisdom: null, action: null },

    cardPublicVersion: false,

    selectedBookmark: 'bm_gold_fleck',

    userConsent: false,

    willingChecked: false,

    currentStudioTask: null,

    currentDraftKey: 'WUTANG-SYN-004'

  };



  // DOM 工具

  function $(id) { return document.getElementById(id); }

  function esc(s) {

    return String(s == null ? '' : s).replace(/[&<>"']/g, function(c) {

      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];

    });

  }

  function strHash(s) {

    var h = 0;

    for (var i = 0; i < s.length; i++) {

      h = (h * 31 + s.charCodeAt(i)) | 0;

    }

    return Math.abs(h);

  }

  function showToast(msg) {

    var t = $('globalToast');

    t.textContent = msg;

    t.classList.add('show');

    setTimeout(function() { t.classList.remove('show'); }, 2200);

  }



  // ==========================================================================

  // 3D Procedural Lotus Particle Bloom Engine (AI 解析过程中的莲花动效)

  // 来自 D:\BaiduSyncdisk\04-WX\萍生解忧\lotus-animation.vue 及 lotus-particle-bloom

  // ==========================================================================

  var lotusEngine = {

    canvas: null,

    ctx: null,

    animId: null,

    isRunning: false,

    width: 360,

    height: 320,

    dpr: 1,

    time: 0,

    lastTime: 0,

    angleY: 0,

    bloomFactor: 0.18,

    targetBloom: 1.0,

    freeParticles: [],

    preset: {

      background: '#06040c',

      particles: ['#ffd700', '#ff8c00', '#ffe4b5', '#ffffff', '#ff4500']

    },

    settings: {

      rotationSpeed: 0.95,

      tiltX: 22,

      tiltY: 0,

      breathingActive: true,

      showPetalCurves: true

    },

    layerConfigs: [

      { count: 6, length: 50, width: 20, tiltBud: 4, tiltBloom: 40, baseRadius: 3, lift: 10 },

      { count: 10, length: 78, width: 25, tiltBud: 12, tiltBloom: 70, baseRadius: 6, lift: 3 },

      { count: 10, length: 78, width: 25, tiltBud: 30, tiltBloom: 80, baseRadius: 12, lift: -6 }

    ],

    quoteTimer: null,

    quoteIndex: 0,

    quotes: [

      "“你听到的声音，其实一直存在于你的沉默里。” —— 鲁米",

      "“每张卡片都不是偶然，它是你在潜意识深处对当下的投影与呼唤。”",

      "“静观卡片，它会带给你早已熟知但长久被繁杂世界遮蔽的内心秘密。”",

      "“当问题被清晰提出的那一刻，答案实际上已经在你的潜意识中悄然成型。”",

      "“先接住情绪，再换个视角，最后走出一小步。”",

      "“我们无需改变外界，只是擦亮明镜，看清内心原本丰饶强大的指路星标。”"

    ],



    init: function(canvasId) {

      if (typeof navigator !== 'undefined' && navigator.userAgent && navigator.userAgent.indexOf('jsdom') !== -1) {

        return;

      }

      var c = document.getElementById(canvasId || 'lotusCanvas');

      if (!c) return;

      this.canvas = c;

      if (!c.getContext) return;

      try {

        this.ctx = c.getContext('2d');

      } catch (e) {

        this.ctx = null;

      }

      this.resize();

    },



    resize: function() {

      if (!this.canvas || !this.ctx) return;

      this.dpr = Math.min(window.devicePixelRatio || 2, 2.5);

      var rect = this.canvas.getBoundingClientRect();

      this.width = (rect && rect.width > 50) ? rect.width : 360;

      this.height = (rect && rect.height > 50) ? rect.height : 320;

      this.canvas.width = this.width * this.dpr;

      this.canvas.height = this.height * this.dpr;

      this.ctx.setTransform(1, 0, 0, 1, 0, 0);

      this.ctx.scale(this.dpr, this.dpr);

    },



    start: function() {

      if (!this.canvas) this.init('lotusCanvas');

      if (!this.canvas || !this.ctx) return;

      this.resize();

      this.isRunning = true;

      this.time = 0;

      this.lastTime = Date.now();

      this.angleY = 0;

      this.bloomFactor = 0.2;

      this.freeParticles = [];

      var self = this;



      this.quoteIndex = 0;

      var qBox = document.getElementById('loadingQuoteBox');

      if (qBox) qBox.textContent = this.quotes[0];

      if (this.quoteTimer) clearInterval(this.quoteTimer);

      this.quoteTimer = setInterval(function() {

        self.quoteIndex = (self.quoteIndex + 1) % self.quotes.length;

        if (qBox) {

          qBox.style.opacity = '0';

          setTimeout(function() {

            qBox.textContent = self.quotes[self.quoteIndex];

            qBox.style.opacity = '1';

          }, 300);

        }

      }, 4200);



      function loop() {

        if (!self.isRunning) return;

        var now = Date.now();

        var delta = now - self.lastTime;

        self.lastTime = now;

        self.time += delta;



        if (self.bloomFactor < self.targetBloom) {

          self.bloomFactor += 0.0026;

          if (self.bloomFactor > self.targetBloom) self.bloomFactor = self.targetBloom;

        }



        self.render(delta);

        self.animId = requestAnimationFrame(loop);

      }

      this.animId = requestAnimationFrame(loop);

    },



    stop: function() {

      this.isRunning = false;

      if (this.animId) {

        cancelAnimationFrame(this.animId);

        this.animId = null;

      }

      if (this.quoteTimer) {

        clearInterval(this.quoteTimer);

        this.quoteTimer = null;

      }

    },



    getProjectedPoint: function(u, vVal, layer, layerIndex, petalOffsetAngle, bloom, breathScale, cameraYaw, pitchAngle, focalLength, cX, cY, isReflected) {

      var length = layer.length;

      var width = layer.width;

      var tiltBud = layer.tiltBud;

      var tiltBloom = layer.tiltBloom;

      var baseRadius = layer.baseRadius;

      var lift = layer.lift;



      var tBudRad = tiltBud * (Math.PI / 180);

      var tBloomRad = tiltBloom * (Math.PI / 180);

      var tiltAngle = tBudRad + (tBloomRad - tBudRad) * bloom;

      var rBase = baseRadius * (1.0 + bloom * 0.42);



      var shapeFactor = Math.sin(Math.pow(u, 0.75) * Math.PI);

      var sideSqueeze = 1.48;

      var widthProfile = shapeFactor * (1.0 - u * 0.12) * sideSqueeze;

      var yLocal = u * length * breathScale * 0.98;



      var baseBend = 0, tipCurl = 0;

      if (layerIndex === 0) {

        baseBend = -20 * Math.sin(u * Math.PI);

        tipCurl = -14 * Math.pow(u, 3.8) * (1.0 - bloom * 0.3);

      } else if (layerIndex === 1) {

        baseBend = -14 * Math.sin(u * Math.PI);

        tipCurl = -5 * Math.pow(u, 3.8) * (1.0 - bloom * 0.3);

      } else {

        baseBend = -4 * Math.sin(u * Math.PI);

        tipCurl = 14 * Math.pow(u, 2.8) * bloom;

      }



      var cupBend = -8 * Math.sin(Math.pow(u, 1.2) * Math.PI) * (1.0 - bloom * 0.4);

      var cupDepth = -(6 + 3 * bloom) * (1.0 - Math.pow(vVal, 2)) * Math.sin(u * Math.PI);

      var zLocal = baseBend + cupBend + tipCurl + cupDepth;



      var xTilt = vVal * widthProfile * width * breathScale;

      var yTilt = yLocal * Math.cos(tiltAngle) - zLocal * Math.sin(tiltAngle) + lift * bloom;

      var zTilt = yLocal * Math.sin(tiltAngle) + zLocal * Math.cos(tiltAngle) + rBase;



      var xFlower = xTilt * Math.cos(petalOffsetAngle) + zTilt * Math.sin(petalOffsetAngle);

      var yFlower = yTilt;

      var zFlower = -xTilt * Math.sin(petalOffsetAngle) + zTilt * Math.cos(petalOffsetAngle);



      if (isReflected) {

        var Y_ground = -12 * (1.0 + bloom * 0.5);

        yFlower = 2 * Y_ground - yFlower;

      }



      var cyY = xFlower * Math.cos(cameraYaw) - zFlower * Math.sin(cameraYaw);

      var czY = xFlower * Math.sin(cameraYaw) + zFlower * Math.cos(cameraYaw);



      var cxP = cyY;

      var cyP = yFlower * Math.cos(pitchAngle) - czY * Math.sin(pitchAngle);

      var czP = yFlower * Math.sin(pitchAngle) + czY * Math.cos(pitchAngle);



      var pScale = focalLength / (focalLength + czP);

      return {

        x: cX + cxP * pScale,

        y: cY - cyP * pScale,

        zDepth: czP,

        scale: pScale

      };

    },



    render: function(delta) {

      var ctx = this.ctx;

      if (!ctx) return;

      var width = this.width;

      var height = this.height;

      var time = this.time;

      var speedScale = Math.min(3, delta / 16.67);



      ctx.clearRect(0, 0, width, height);



      var bloom = this.bloomFactor;

      this.angleY += this.settings.rotationSpeed * 0.016 * speedScale;

      var baseRotationAngle = this.angleY;



      var pitchAngle = this.settings.tiltX * (Math.PI / 180);

      var cameraYaw = this.settings.tiltY * (Math.PI / 180);



      var cX = width / 2;

      var cY = height / 2 + 10;

      var focalLength = 580;



      var breathScale = 1.0;

      var auraIntensity = 1.0;

      if (this.settings.breathingActive) {

        var breatheRate = time * 0.0011;

        var breathCycleValue = (Math.sin(breatheRate) + 1) / 2;

        breathScale = 1.0 + breathCycleValue * 0.16;

        auraIntensity = 0.6 + breathCycleValue * 0.6;

      }



      var maxUSteps = 14;

      var self = this;



      // 1. Water reflection

      this.layerConfigs.forEach(function(layer, layerIndex) {

        var count = layer.count;

        for (var pIdx = 0; pIdx < count; pIdx++) {

          var petalOffsetAngle = (pIdx / count) * Math.PI * 2 + baseRotationAngle;

          var refLeftPoints = [];

          var refRightPoints = [];



          for (var uIdx = 0; uIdx <= maxUSteps; uIdx++) {

            var u = uIdx / maxUSteps;

            refLeftPoints.push(self.getProjectedPoint(u, -1, layer, layerIndex, petalOffsetAngle, bloom, breathScale, cameraYaw, pitchAngle, focalLength, cX, cY, true));

            refRightPoints.push(self.getProjectedPoint(u, 1, layer, layerIndex, petalOffsetAngle, bloom, breathScale, cameraYaw, pitchAngle, focalLength, cX, cY, true));

          }



          ctx.beginPath();

          ctx.moveTo(refLeftPoints[0].x, refLeftPoints[0].y);

          for (var i = 1; i <= maxUSteps; i++) ctx.lineTo(refLeftPoints[i].x, refLeftPoints[i].y);

          for (var j = maxUSteps; j >= 0; j--) ctx.lineTo(refRightPoints[j].x, refRightPoints[j].y);

          ctx.closePath();



          var refFill = ctx.createLinearGradient(cX, cY - 20, cX, height);

          refFill.addColorStop(0, 'rgba(220, 80, 20, ' + (0.04 * auraIntensity) + ')');

          refFill.addColorStop(0.3, 'rgba(255, 160, 40, ' + (0.015 * auraIntensity) + ')');

          refFill.addColorStop(0.6, 'rgba(0,0,0,0)');

          ctx.fillStyle = refFill;

          ctx.fill();

        }

      });



      // 2. Depth sort petals and core

      var renderItems = [];

      this.layerConfigs.forEach(function(layer, layerIndex) {

        var count = layer.count;

        for (var pIdx = 0; pIdx < count; pIdx++) {

          var petalOffsetAngle = (pIdx / count) * Math.PI * 2 + baseRotationAngle;

          var centerPt = self.getProjectedPoint(0.5, 0, layer, layerIndex, petalOffsetAngle, bloom, breathScale, cameraYaw, pitchAngle, focalLength, cX, cY, false);

          renderItems.push({

            type: 'petal',

            layerIndex: layerIndex,

            pIdx: pIdx,

            petalOffsetAngle: petalOffsetAngle,

            layer: layer,

            depth: centerPt.zDepth

          });

        }

      });



      var corePt = this.getProjectedPoint(0, 0, { length: 0, width: 0, tiltBud: 0, tiltBloom: 0, baseRadius: 0, lift: 0 }, 0, 0, bloom, breathScale, cameraYaw, pitchAngle, focalLength, cX, cY, false);

      renderItems.push({

        type: 'core',

        x: corePt.x,

        y: corePt.y,

        depth: corePt.zDepth

      });



      renderItems.sort(function(a, b) { return b.depth - a.depth; });



      // 3. Render items

      renderItems.forEach(function(item) {

        if (item.type === 'core') {

          var scX = item.x, scY = item.y;

          var glow = ctx.createRadialGradient(scX, scY, 0, scX, scY, 44 * auraIntensity);

          glow.addColorStop(0, 'rgba(255, 190, 80, 0.45)');

          glow.addColorStop(0.3, 'rgba(255, 110, 30, 0.2)');

          glow.addColorStop(0.7, 'rgba(255, 70, 10, 0.05)');

          glow.addColorStop(1, 'rgba(0,0,0,0)');

          ctx.fillStyle = glow;

          ctx.beginPath();

          ctx.arc(scX, scY, 48 * auraIntensity, 0, Math.PI * 2);

          ctx.fill();



          var innerGlow = ctx.createRadialGradient(scX, scY, 0, scX, scY, 15);

          innerGlow.addColorStop(0, '#ffffff');

          innerGlow.addColorStop(0.3, 'rgba(255, 240, 180, 0.95)');

          innerGlow.addColorStop(0.7, 'rgba(255, 180, 50, 0.3)');

          innerGlow.addColorStop(1, 'rgba(0,0,0,0)');

          ctx.fillStyle = innerGlow;

          ctx.beginPath();

          ctx.arc(scX, scY, 16, 0, Math.PI * 2);

          ctx.fill();

        } else if (item.type === 'petal') {

          var leftPoints = [];

          var rightPoints = [];



          for (var uIdx = 0; uIdx <= maxUSteps; uIdx++) {

            var u = uIdx / maxUSteps;

            leftPoints.push(self.getProjectedPoint(u, -1, item.layer, item.layerIndex, item.petalOffsetAngle, bloom, breathScale, cameraYaw, pitchAngle, focalLength, cX, cY, false));

            rightPoints.push(self.getProjectedPoint(u, 1, item.layer, item.layerIndex, item.petalOffsetAngle, bloom, breathScale, cameraYaw, pitchAngle, focalLength, cX, cY, false));

          }



          ctx.beginPath();

          ctx.moveTo(leftPoints[0].x, leftPoints[0].y);

          for (var i = 1; i <= maxUSteps; i++) ctx.lineTo(leftPoints[i].x, leftPoints[i].y);

          for (var j = maxUSteps; j >= 0; j--) ctx.lineTo(rightPoints[j].x, rightPoints[j].y);

          ctx.closePath();



          var basePt = leftPoints[0];

          var tipPt = leftPoints[maxUSteps];



          var fillGrad = ctx.createLinearGradient(basePt.x, basePt.y, tipPt.x, tipPt.y);

          fillGrad.addColorStop(0, 'rgba(210, 80, 20, ' + (0.10 * auraIntensity) + ')');

          fillGrad.addColorStop(0.35, 'rgba(255, 175, 45, ' + (0.18 * auraIntensity) + ')');

          fillGrad.addColorStop(0.7, 'rgba(255, 240, 200, ' + (0.22 * auraIntensity) + ')');

          fillGrad.addColorStop(1, 'rgba(255, 255, 255, ' + (0.32 * auraIntensity) + ')');

          ctx.fillStyle = fillGrad;

          ctx.fill();



          if (self.settings.showPetalCurves) {

            var strokeGrad = ctx.createLinearGradient(basePt.x, basePt.y, tipPt.x, tipPt.y);

            strokeGrad.addColorStop(0, 'rgba(255, 110, 20, ' + (0.35 * auraIntensity) + ')');

            strokeGrad.addColorStop(0.4, 'rgba(255, 200, 60, ' + (0.70 * auraIntensity) + ')');

            strokeGrad.addColorStop(0.75, 'rgba(255, 245, 210, ' + (0.90 * auraIntensity) + ')');

            strokeGrad.addColorStop(1, 'rgba(255, 255, 255, ' + (1.0 * auraIntensity) + ')');

            ctx.strokeStyle = strokeGrad;

            ctx.lineWidth = 0.8;

            ctx.stroke();

          }



          // Longitudinal veins

          [-0.5, 0, 0.5].forEach(function(v) {

            ctx.beginPath();

            var pStart = self.getProjectedPoint(0.05, v, item.layer, item.layerIndex, item.petalOffsetAngle, bloom, breathScale, cameraYaw, pitchAngle, focalLength, cX, cY, false);

            ctx.moveTo(pStart.x, pStart.y);

            for (var uIdx = 1; uIdx <= maxUSteps; uIdx++) {

              var u = uIdx / maxUSteps;

              var pt = self.getProjectedPoint(u, v, item.layer, item.layerIndex, item.petalOffsetAngle, bloom, breathScale, cameraYaw, pitchAngle, focalLength, cX, cY, false);

              ctx.lineTo(pt.x, pt.y);

            }

            var vGrad = ctx.createLinearGradient(pStart.x, pStart.y, tipPt.x, tipPt.y);

            vGrad.addColorStop(0, 'rgba(255, 120, 30, 0)');

            vGrad.addColorStop(0.3, 'rgba(255, 180, 50, ' + (0.16 * auraIntensity) + ')');

            vGrad.addColorStop(0.75, 'rgba(255, 240, 190, ' + (0.32 * auraIntensity) + ')');

            vGrad.addColorStop(1, 'rgba(255, 255, 255, ' + (0.42 * auraIntensity) + ')');

            ctx.strokeStyle = vGrad;

            ctx.lineWidth = 0.45;

            ctx.stroke();

          });



          // Petal sparkles

          for (var s = 0; s < 4; s++) {

            var seed = (item.layerIndex * 313 + item.pIdx * 97 + s * 43) % 4000;

            var prng = function(val) { var x = Math.sin(val) * 10000; return x - Math.floor(x); };

            var uS = 0.25 + 0.6 * prng(seed + 1.1);

            var vS = -0.6 + 1.2 * prng(seed + 0.5);

            var ptS = self.getProjectedPoint(uS, vS, item.layer, item.layerIndex, item.petalOffsetAngle, bloom, breathScale, cameraYaw, pitchAngle, focalLength, cX, cY, false);

            var blink = (Math.sin(time * 0.003 + seed) + 1) / 2;

            var alpha = (0.2 + blink * 0.8) * auraIntensity;

            if (alpha > 0.15) {

              ctx.fillStyle = 'rgba(255, 245, 210, ' + alpha + ')';

              ctx.beginPath();

              ctx.arc(ptS.x, ptS.y, 0.8 + blink * 0.7, 0, Math.PI * 2);

              ctx.fill();

              if (blink > 0.8) {

                ctx.strokeStyle = 'rgba(255, 255, 255, ' + ((blink - 0.8) * 5 * alpha) + ')';

                ctx.lineWidth = 0.4;

                ctx.beginPath();

                ctx.moveTo(ptS.x - 3, ptS.y); ctx.lineTo(ptS.x + 3, ptS.y);

                ctx.moveTo(ptS.x, ptS.y - 3); ctx.lineTo(ptS.x, ptS.y + 3);

                ctx.stroke();

              }

            }

          }

        }

      });



      // 4. Floating Ember Particles

      if (Math.random() < 0.25 && this.freeParticles.length < 80) {

        this.freeParticles.push({

          x: (Math.random() - 0.5) * 150,

          y: 20 + (Math.random() - 0.5) * 50,

          z: (Math.random() - 0.5) * 150,

          vx: (Math.random() - 0.5) * 0.3,

          vy: -0.4 - Math.random() * 0.4,

          vz: (Math.random() - 0.5) * 0.3,

          life: 0,

          maxLife: 85 + Math.random() * 40,

          color: this.preset.particles[Math.floor(Math.random() * this.preset.particles.length)]

        });

      }



      var activeP = [];

      this.freeParticles.forEach(function(p) {

        p.life += 1;

        if (p.life >= p.maxLife) return;

        p.x += p.vx * speedScale;

        p.y += p.vy * speedScale;

        p.z += p.vz * speedScale;



        var fYawX = p.x * Math.cos(cameraYaw) - p.z * Math.sin(cameraYaw);

        var fYawZ = p.x * Math.sin(cameraYaw) + p.z * Math.cos(cameraYaw);

        var fPitchY = p.y * Math.cos(pitchAngle) - fYawZ * Math.sin(pitchAngle);

        var fPitchZ = p.y * Math.sin(pitchAngle) + fYawZ * Math.cos(pitchAngle);



        var pScale = focalLength / (focalLength + fPitchZ);

        var tx = cX + fYawX * pScale;

        var ty = cY - fPitchY * pScale;



        var ratio = p.life / p.maxLife;

        var shimmer = (Math.sin(time * 0.015 + p.x) + 1) / 2;

        var alpha = Math.sin(ratio * Math.PI) * (0.25 + shimmer * 0.65);



        if (tx >= 0 && tx <= width && ty >= 0 && ty <= height) {

          ctx.globalAlpha = alpha;

          ctx.fillStyle = p.color;

          ctx.beginPath();

          ctx.arc(tx, ty, 0.9 + shimmer * 0.8, 0, Math.PI * 2);

          ctx.fill();

          activeP.push(p);

        }

      });

      ctx.globalAlpha = 1.0;

      this.freeParticles = activeP;

    }

  };



  // ================= 风险评估与分流 (PRD 4.4 / F-02) =================

  function evaluateRisk(text) {

    var t = String(text || '');

    for (var i = 0; i < RISK_HIGH.length; i++) {

      if (t.indexOf(RISK_HIGH[i]) >= 0) {

        return { level: 'high_risk', match: RISK_HIGH[i] };

      }

    }

    for (var k = 0; k < RISK_PATTERNS.length; k++) {

      if (RISK_PATTERNS[k].test(t)) {

        return { level: 'high_risk', match: '句式模式命中' };

      }

    }

    for (var j = 0; j < RISK_REVIEW.length; j++) {

      if (t.indexOf(RISK_REVIEW[j]) >= 0) {

        return { level: 'review', match: RISK_REVIEW[j] };

      }

    }

    return { level: 'normal', match: '' };

  }



  // ================= 场景自动定位 =================

  var SCENARIO_KEYWORDS = {

    work: ['工作', '职场', '领导', '老板', '同事', '绩效', 'KPI', '考核', '加班', '辞职', '裁员', '面试', '晋升', '项目', '汇报', '批评', '内耗', '上班', '打工', '班味', '离职', '跳槽', '工资', '部门', '方案'],

    relation: ['关系', '父母', '妈妈', '爸爸', '妈', '爸', '婆婆', '公公', '老公', '老婆', '伴侣', '男朋友', '女朋友', '对象', '朋友', '催婚', '催', '亲戚', '家人', '拒绝', '讨好', '边界', '冷战', '吵架', '分手', '结婚', '家庭'],

    night: ['睡', '失眠', '半夜', '凌晨', '晚上', '夜里', '反刍', '想不通', '反复', '后悔', '焦虑', '明天', '未来', '担心', '心慌', '停不下来', '睡不着', '噩梦'],

    growth: ['拖延', '完美', '开始', '方向', '迷茫', '目标', '自律', '成长', '学习', '考试', '计划', '改变', '自我', '懒', '动力', '意义', '坚持', '突破']

  };



  function detectScenario(text, manualTag) {

    if (manualTag) return manualTag;

    var t = String(text || ''), best = 'work', maxHits = 0;

    Object.keys(SCENARIO_KEYWORDS).forEach(function(k) {

      var count = 0;

      SCENARIO_KEYWORDS[k].forEach(function(kw) {

        if (t.indexOf(kw) >= 0) count++;

      });

      if (count > maxHits) { maxHits = count; best = k; }

    });

    return best;

  }



  // ================= 经典语料检索 (Skill 2) =================

  function retrieveClassic(scenario, text) {

    var t = String(text || '');

    var pool = CLASSICS.filter(function(c) { return c.status !== 'not_found'; });

    var scored = pool.map(function(c) {

      var s = 0;

      if (String(c.scenarios || '').split(';').indexOf(scenario) >= 0) s += 6;

      String(c.themes || '').split(';').forEach(function(th) {

        if (th && t.indexOf(th) >= 0) s += 4;

      });

      if (c.status === 'verified') s += 2;

      return { c: c, score: s };

    }).sort(function(a, b) { return b.score - a.score; });



    var topScore = scored.length ? scored[0].score : 0;

    var candidates = scored.filter(function(x) { return x.score >= topScore - 2 && x.score > 0; });

    if (!candidates.length) candidates = scored.slice(0, 4);

    if (!candidates.length) return null;



    var idx = strHash(t + scenario) % candidates.length;

    return candidates[idx].c;

  }



  // ================= 共情库与四步构建 =================

  var EMPATHY_TEMPLATES = {

    work: [

      '你写到「{q}」。真正磨人的，可能不是那点事本身，而是它让你开始怀疑自己——是不是我不够好。这种消耗，比加班更让人疲惫。',

      '「{q}」——听起来你已经一个人撑了很久。你不是不想做好，而是那些沉重的负担里，有一部分本就不该全部由你来扛。',

      '你把这件事说出来，说明它已经在你心里转了很久。「{q}」，这种说不出口的憋闷，悟堂懂你。'

    ],

    relation: [

      '你写到「{q}」。难的也许不是那件事本身，而是它戳到了「我是不是不重要、不被在乎」这一下。',

      '「{q}」——一边是重要的人际关系，一边是你自己的真实感受，夹在中间怎么做都像是错的。',

      '听起来你不是不在乎对方，恰恰是太在乎了，才习惯性地把自己放到了最后。「{q}」。'

    ],

    night: [

      '「{q}」——白天能压住的东西，到了夜深人静全浮上来了。这不是你脆弱，是大脑在夜里本来就会放大所有担忧。',

      '你写到「{q}」。夜里反复想同一件事，说明它对你真的很重要，而不是你想不开。',

      '夜里思绪停不下来，往往不是因为问题解决不了，而是你太累了，累到没有力气把它想完。'

    ],

    growth: [

      '你写到「{q}」。你可能不是拖延或懒，恰恰是太想把它做完美了，以至于连开始都需要巨大的勇气。',

      '「{q}」——心里很急，身体却动不了，然后又陷入更深的自责，这种内耗很多人都经历过。',

      '你能把这句话写下来，本身就已经是一个了不起的开始。至少你愿意温柔地正视它了。'

    ]

  };



  function snippet(text, maxLen) {

    var t = String(text || '').replace(/\s+/g, ' ').trim();

    maxLen = maxLen || 22;

    return t.length <= maxLen ? t : t.slice(0, maxLen) + '…';

  }



  function generateEmpathy(scenario, text) {

    var list = EMPATHY_TEMPLATES[scenario] || EMPATHY_TEMPLATES.growth;

    var idx = strHash(text + scenario) % list.length;

    return list[idx].replace('{q}', snippet(text));

  }



  var FURTHER_MAP = {

    work: '读完原文那一段，再回到今天这件事上：分清哪些是客观事实，哪些是他人的主观评价，哪些是你今天就能掌控的一步。',

    relation: '读的时候留意一句话：这段关系是在滋养你，还是在不断掏空你的边界。',

    night: '睡前读一小段即可，读完就合上书。今晚让文字替你分担那些繁杂思绪。',

    growth: '读三五分钟就够。重点不是一次读懂多少，而是让手先轻松地动起来。'

  };



  var THEME_MAP = {

    work: '去班味 · 职场与评价',

    relation: '松绑 · 关系与边界',

    night: '安住 · 深夜思绪',

    growth: '破局 · 行动与自我'

  };



  function matchReliefCards(scenario, text, presetMindset) {

    var t = String(text || '').toLowerCase();



    // 1. 心境牌 (Mindset)

    var mindsetCard = presetMindset;

    if (!mindsetCard) {

      var mCandidates = CARDS_MINDSET.map(function(card) {

        var score = 0;

        if (card.scenarios && card.scenarios.indexOf(scenario) >= 0) score += 6;

        if (card.keywords) {

          card.keywords.forEach(function(kw) {

            if (t.indexOf(kw.toLowerCase()) >= 0) score += 3;

          });

        }

        return { card: card, score: score };

      }).sort(function(a, b) { return b.score - a.score; });

      var topMScore = mCandidates.length ? mCandidates[0].score : 0;

      var topMCards = mCandidates.filter(function(x) { return x.score >= topMScore - 1 && x.score > 0; });

      if (!topMCards.length) topMCards = mCandidates;

      var mIdx = strHash(t + scenario + 'm') % Math.max(1, topMCards.length);

      mindsetCard = topMCards[mIdx] ? topMCards[mIdx].card : CARDS_MINDSET[0];

    }



    // 2. 东方智慧牌 (Wisdom)

    var wisdomCard = null;

    if (mindsetCard && mindsetCard.recommended_wisdom_cards && mindsetCard.recommended_wisdom_cards.length > 0) {

      var recId = mindsetCard.recommended_wisdom_cards[strHash(t) % mindsetCard.recommended_wisdom_cards.length];

      for (var i = 0; i < CARDS_WISDOM.length; i++) {

        if (CARDS_WISDOM[i].id === recId) {

          wisdomCard = CARDS_WISDOM[i];

          break;

        }

      }

    }

    if (!wisdomCard) {

      var wCandidates = CARDS_WISDOM.filter(function(w) {

        return w.scenarios && w.scenarios.indexOf(scenario) >= 0;

      });

      if (!wCandidates.length) wCandidates = CARDS_WISDOM;

      var wIdx = strHash(t + scenario + 'w') % Math.max(1, wCandidates.length);

      wisdomCard = wCandidates[wIdx] || CARDS_WISDOM[0];

    }



    // 3. 行动牌 (Action)

    var actionCard = null;

    if (mindsetCard && mindsetCard.recommended_action_cards && mindsetCard.recommended_action_cards.length > 0) {

      var recActId = mindsetCard.recommended_action_cards[strHash(t) % mindsetCard.recommended_action_cards.length];

      for (var j = 0; j < CARDS_ACTION.length; j++) {

        if (CARDS_ACTION[j].id === recActId) {

          actionCard = CARDS_ACTION[j];

          break;

        }

      }

    }

    if (!actionCard) {

      var aCandidates = CARDS_ACTION.filter(function(a) {

        return a.scenarios && a.scenarios.indexOf(scenario) >= 0;

      });

      if (!aCandidates.length) aCandidates = CARDS_ACTION;

      var aIdx = strHash(t + scenario + 'a') % Math.max(1, aCandidates.length);

      actionCard = aCandidates[aIdx] || CARDS_ACTION[0];

    }



    return {

      mindset: mindsetCard,

      wisdom: wisdomCard,

      action: actionCard

    };

  }



  function changeSingleCard(type) {

    if (!appState.currentCards) return;

    var t = $('userTextarea').value.trim();

    var scenario = appState.selectedScenario || 'work';



    if (type === 'mindset') {

      var currentId = appState.currentCards.mindset ? appState.currentCards.mindset.id : '';

      var mPool = CARDS_MINDSET.filter(function(c) { return c.id !== currentId; });

      if (mPool.length > 0) {

        var nextM = mPool[strHash(currentId + Date.now().toString()) % mPool.length];

        appState.currentCards.mindset = nextM;

        if (appState.currentResult) {

          appState.currentResult.empathy = generateEmpathy(scenario, t) + '（心境牌：' + nextM.title + '）';

        }

        renderReliefCards(appState.currentCards);

        renderFourStepList(appState.currentResult);

        showToast('已更换心境牌：' + nextM.title);

      }

    } else if (type === 'wisdom') {

      var curWId = appState.currentCards.wisdom ? appState.currentCards.wisdom.id : '';

      var wPool = CARDS_WISDOM.filter(function(c) { return c.id !== curWId; });

      if (wPool.length > 0) {

        var nextW = wPool[strHash(curWId + Date.now().toString()) % wPool.length];

        appState.currentCards.wisdom = nextW;

        if (appState.currentResult) {

          appState.currentResult.classic = {

            quote: nextW.classic_source.quote,

            book: nextW.classic_source.book,

            chapter: nextW.classic_source.chapter,

            source_id: nextW.id,

            verification_status: nextW.verification_status || 'verified'

          };

          appState.currentResult.classic_obj = {

            id: nextW.id,

            book: nextW.classic_source.book,

            chapter: nextW.classic_source.chapter,

            era_author: nextW.classic_source.author,

            quote: nextW.classic_source.quote,

            translation: nextW.classic_source.translation,

            edition: nextW.classic_source.edition,

            note: nextW.classic_source.note,

            status: nextW.verification_status || 'verified'

          };

          appState.currentResult.modern_interp = nextW.modern_interpretation;

          appState.currentResult.further_reading = '推荐阅读《' + nextW.classic_source.book + '》' + (nextW.classic_source.chapter && nextW.classic_source.chapter !== '—' ? '·' + nextW.classic_source.chapter : '') + '。' + (FURTHER_MAP[scenario] || '');

        }

        renderReliefCards(appState.currentCards);

        renderFourStepList(appState.currentResult);

        showToast('已更换东方智慧牌：《' + nextW.classic_source.book + '》');

      }

    } else if (type === 'action') {

      var curAId = appState.currentCards.action ? appState.currentCards.action.id : '';

      var aPool = CARDS_ACTION.filter(function(c) { return c.id !== curAId; });

      if (aPool.length > 0) {

        var nextA = aPool[strHash(curAId + Date.now().toString()) % aPool.length];

        appState.currentCards.action = nextA;

        if (appState.currentResult) {

          appState.currentResult.micro_action = {

            headline: nextA.title,

            steps: nextA.steps

          };

        }

        renderReliefCards(appState.currentCards);

        renderFourStepList(appState.currentResult);

        showToast('已更换行动牌：' + nextA.title);

      }

    }

  }



  function renderReliefCards(cards) {

    if (!cards || !cards.mindset || !cards.wisdom || !cards.action) return;

    var m = cards.mindset;

    var w = cards.wisdom;

    var a = cards.action;

    var mQuote = m.front_text || m.quote || '';

    var mDesc = m.short_description || m.sample_prompt || m.subtitle || '';



    // 01 心境牌

    $('resCardMindset').innerHTML = ''

      + '<div class="card-3d-inner">'

      + '  <div class="card-3d-face card-3d-back">'

      + '    <div class="card-corner tl"></div><div class="card-corner tr"></div>'

      + '    <div class="card-corner bl"></div><div class="card-corner br"></div>'

      + '    <div class="card-back-header">SUBCONSCIOUS</div>'

      + '    <div class="card-back-center">'

      + '      <div class="card-orbit-ring"></div>'

      + '      <div class="card-orbit-ring-inner"></div>'

      + '      <div class="card-starburst">'

      + '        <div class="card-starburst-ray v"></div>'

      + '        <div class="card-starburst-ray h"></div>'

      + '        <div class="card-starburst-ray d1"></div>'

      + '        <div class="card-starburst-ray d2"></div>'

      + '        <div class="card-core-gem">悟</div>'

      + '      </div>'

      + '    </div>'

      + '    <div class="card-back-footer">'

      + '      <span>01 当下投影 · 心境牌</span>'

      + '      <span class="tap-hint">点击翻开 ↺</span>'

      + '    </div>'

      + '  </div>'

      + '  <div class="card-3d-face card-3d-front">'

      + '    <div>'

      + '      <div class="relief-card-header">'

      + '        <span class="card-front-tag mindset">01 心境牌 · 当下投影</span>'

      + '        <button class="btn-card-op" id="btnChangeMindset">换一张 ↻</button>'

      + '      </div>'

      + '      <div class="card-front-title serif">' + esc(m.title) + '</div>'

      + (mQuote ? ('      <div class="card-front-quote">「' + esc(mQuote) + '」</div>') : '')

      + (mDesc ? ('      <div class="card-front-sub">' + esc(mDesc) + '</div>') : '')

      + '    </div>'

      + '    <div>'

      + '      <div class="card-front-meta">'

      + '        <span>维度：' + esc(m.dimension || '认知反思') + '</span>'

      + '        <span style="color:var(--color-gold);font-size:11px;">↺ 3D翻面</span>'

      + '      </div>'

      + '    </div>'

      + '  </div>'

      + '</div>';



    // 02 智慧牌

    var wSrc = w.classic_source || {};

    var sage = getSageInfo(wSrc.author, wSrc.book);

    var avatarMini = sage.b64

      ? '<img src="' + sage.b64 + '" alt="' + esc(sage.name) + '" style="width:22px;height:22px;border-radius:4px;box-shadow:0 1px 2px rgba(0,0,0,0.1);">'

      : '';



    $('resCardWisdom').innerHTML = ''

      + '<div class="card-3d-inner">'

      + '  <div class="card-3d-face card-3d-back">'

      + '    <div class="card-corner tl"></div><div class="card-corner tr"></div>'

      + '    <div class="card-corner bl"></div><div class="card-corner br"></div>'

      + '    <div class="card-back-header">SUBCONSCIOUS</div>'

      + '    <div class="card-back-center">'

      + '      <div class="card-orbit-ring"></div>'

      + '      <div class="card-orbit-ring-inner"></div>'

      + '      <div class="card-starburst">'

      + '        <div class="card-starburst-ray v"></div>'

      + '        <div class="card-starburst-ray h"></div>'

      + '        <div class="card-starburst-ray d1"></div>'

      + '        <div class="card-starburst-ray d2"></div>'

      + '        <div class="card-core-gem">悟</div>'

      + '      </div>'

      + '    </div>'

      + '    <div class="card-back-footer">'

      + '      <span>02 潜意盲区 · 智慧牌</span>'

      + '      <span class="tap-hint">点击翻开 ↺</span>'

      + '    </div>'

      + '  </div>'

      + '  <div class="card-3d-face card-3d-front">'

      + '    <div>'

      + '      <div class="relief-card-header">'

      + '        <span class="card-front-tag wisdom">02 东方智慧 · 潜意盲区</span>'

      + '        <button class="btn-card-op" id="btnChangeWisdom">换一张 ↻</button>'

      + '      </div>'

      + '      <div class="card-front-title serif" style="font-size:15.5px;">「' + esc(wSrc.quote || w.title) + '」</div>'

      + '      <div class="card-front-sub" style="margin-top:6px;font-size:12.5px;color:var(--color-ink-light);line-height:1.55;">'

      + '        <strong>视角：</strong>' + esc(w.modern_interpretation || '')

      + '      </div>'

      + '    </div>'

      + '    <div>'

      + '      <div class="card-front-meta">'

      + '        <div style="display:flex;align-items:center;gap:6px;">'

      +            avatarMini

      + '          <span style="max-width:140px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">《' + esc(wSrc.book || '经典') + '》' + (wSrc.chapter && wSrc.chapter !== '—' ? ' · ' + esc(wSrc.chapter) : '') + '</span>'

      + '        </div>'

      + '        <span class="badge ok" style="font-size:10px;">已核验</span>'

      + '      </div>'

      + '      <div style="text-align:right;margin-top:4px;">'

      + '        <span style="font-size:11px;color:var(--color-gold);">↺ 3D翻面</span>'

      + '      </div>'

      + '    </div>'

      + '  </div>'

      + '</div>';



    // 03 行动牌

    var stepsList = (a.steps || []).map(function(s) {

      return '<div style="margin-bottom:3px;">• ' + esc(s) + '</div>';

    }).join('');

    var altText = (a.alternatives && a.alternatives.length > 0)

      ? '备选微步：' + esc(a.alternatives[0])

      : '如果今天不想动：闭目做三次匀速深呼吸，允许自己停下来。';



    $('resCardAction').innerHTML = ''

      + '<div class="card-3d-inner">'

      + '  <div class="card-3d-face card-3d-back">'

      + '    <div class="card-corner tl"></div><div class="card-corner tr"></div>'

      + '    <div class="card-corner bl"></div><div class="card-corner br"></div>'

      + '    <div class="card-back-header">SUBCONSCIOUS</div>'

      + '    <div class="card-back-center">'

      + '      <div class="card-orbit-ring"></div>'

      + '      <div class="card-orbit-ring-inner"></div>'

      + '      <div class="card-starburst">'

      + '        <div class="card-starburst-ray v"></div>'

      + '        <div class="card-starburst-ray h"></div>'

      + '        <div class="card-starburst-ray d1"></div>'

      + '        <div class="card-starburst-ray d2"></div>'

      + '        <div class="card-core-gem">悟</div>'

      + '      </div>'

      + '    </div>'

      + '    <div class="card-back-footer">'

      + '      <span>03 指引路径 · 行动牌</span>'

      + '      <span class="tap-hint">点击翻开 ↺</span>'

      + '    </div>'

      + '  </div>'

      + '  <div class="card-3d-face card-3d-front">'

      + '    <div>'

      + '      <div class="relief-card-header">'

      + '        <span class="card-front-tag action">03 微行动 · 指引路径</span>'

      + '        <button class="btn-card-op" id="btnChangeAction">换一个 ↻</button>'

      + '      </div>'

      + '      <div class="card-front-title serif">' + esc(a.title) + '</div>'

      + '      <div class="card-front-sub" style="font-size:12.5px;line-height:1.55;">' + stepsList + '</div>'

      + '      <div style="margin-top:6px;font-size:11.5px;color:var(--color-muted);background:var(--color-bg);padding:4px 6px;border-radius:4px;border:1px solid var(--color-border);line-height:1.4;">'

      +          altText

      + '      </div>'

      + '    </div>'

      + '    <div>'

      + '      <div class="card-front-meta" style="margin-bottom:8px;">'

      + '        <span>约 ' + esc(a.time_estimate_min || 5) + ' 分钟</span>'

      + '        <span>阻力：' + esc(a.friction_level || '低') + '</span>'

      + '      </div>'

      + '      <div style="display:flex;gap:6px;flex-wrap:wrap;">'

      + '        <button class="btn sm' + (appState.willingChecked ? ' checked' : '') + '" id="btnWillingTryCard" style="font-size:11.5px;padding:4px 10px;">'

      + (appState.willingChecked ? '✓ 已记下' : '我愿意试试')

      + '        </button>'

      + '        <button class="btn sm secondary" id="btnNotToday" style="font-size:11.5px;padding:4px 8px;">今晚先不试</button>'

      + '      </div>'

      + '      <div style="text-align:right;margin-top:4px;">'

      + '        <span style="font-size:11px;color:var(--color-gold);">↺ 3D翻面</span>'

      + '      </div>'

      + '    </div>'

      + '  </div>'

      + '</div>';



    // 绑定内部交互 (阻止冒泡翻牌)

    $('btnChangeMindset').onclick = function(e) { e.stopPropagation(); changeSingleCard('mindset'); };

    $('btnChangeWisdom').onclick = function(e) { e.stopPropagation(); changeSingleCard('wisdom'); };

    $('btnChangeAction').onclick = function(e) { e.stopPropagation(); changeSingleCard('action'); };



    $('btnWillingTryCard').onclick = function(e) {

      e.stopPropagation();

      appState.willingChecked = !appState.willingChecked;

      renderReliefCards(appState.currentCards);

      renderFourStepList(appState.currentResult);

      if (appState.willingChecked) {

        showToast('愿这一步，为你带去一点轻盈与力量');

      }

    };



    $('btnNotToday').onclick = function(e) {

      e.stopPropagation();

      showToast('好的，今晚先好好休息，不给自己任何负担也是一种智慧。');

    };

  }



  function assembleFourStep(caseId, scenario, text, cards) {

    var cObj = null, classicRef = null, modInterp = '';



    if (cards && cards.wisdom && cards.wisdom.classic_source) {

      var ws = cards.wisdom.classic_source;

      classicRef = {

        quote: ws.quote,

        book: ws.book,

        chapter: ws.chapter,

        source_id: cards.wisdom.id,

        verification_status: cards.wisdom.verification_status || 'verified'

      };

      cObj = {

        id: cards.wisdom.id,

        book: ws.book,

        chapter: ws.chapter,

        era_author: ws.author,

        quote: ws.quote,

        translation: ws.translation,

        edition: ws.edition,

        note: ws.note,

        status: cards.wisdom.verification_status || 'verified'

      };

      modInterp = cards.wisdom.modern_interpretation;

    } else {

      var c = retrieveClassic(scenario, text);

      if (!c) {

        classicRef = {

          quote: '',

          book: '悟堂典籍库',

          chapter: '—',

          source_id: 'NONE',

          verification_status: 'not_found'

        };

        modInterp = '本次检索未找到足够严密对应的古人直接引言。与其编造看似古风的话，我们更愿意直接告诉你：此时此刻心乱是极正常的，先把脚步慢下来。';

      } else {

        classicRef = {

          quote: c.quote,

          book: c.book,

          chapter: c.chapter,

          source_id: c.id,

          verification_status: c.status

        };

        cObj = c;

        modInterp = c.interpretation;

      }

    }



    var actHeadline = (cards && cards.action) ? cards.action.title : '今晚 5 分钟微行动';

    var actSteps = (cards && cards.action) ? cards.action.steps : ['静坐深呼吸2分钟'];



    var empathyText = generateEmpathy(scenario, text);

    if (cards && cards.mindset) {

      empathyText += ' 当下你所体会的，可能正如这句觉察：「' + cards.mindset.quote + '」。';

    }



    return {

      case_id: caseId,

      scenario: scenario,

      theme_title: THEME_MAP[scenario] || '东方启发视角',

      empathy: empathyText,

      classic: classicRef,

      classic_obj: cObj,

      modern_interp: modInterp,

      micro_action: {

        headline: actHeadline,

        steps: actSteps

      },

      further_reading: classicRef && classicRef.book && classicRef.verification_status === 'verified'

        ? '推荐阅读《' + classicRef.book + '》' + (classicRef.chapter && classicRef.chapter !== '—' ? '·' + classicRef.chapter : '') + '。' + (FURTHER_MAP[scenario] || '')

        : '暂无特定典籍章节推荐；以今晚微行动为主。',

      safety_note: '若这种低落或内耗持续并影响作息，向信任之人或专业人士倾诉，会比独自承受更有力量。'

    };

  }



  // ================= 渲染四步回应与解忧卡牌 (PRD 2.0 F-04 & F-05) =================

  var BADGE_CONFIG = {

    verified: { cls: 'ok', text: '出处已核验' },

    needs_review: { cls: 'rev', text: '待复核·辑录' },

    not_found: { cls: 'nf', text: '未找到可靠出处' }

  };



  function renderFourStepList(r) {

    if (!r) return;

    var c = r.classic;

    var b = BADGE_CONFIG[c.verification_status] || BADGE_CONFIG.not_found;

    var cObj = r.classic_obj;



    var quoteHtml = '';

    if (c.quote) {

      var sage = getSageInfo(cObj ? cObj.era_author : '', c.book);

      var avatarImg = sage.b64

        ? '<img src="' + sage.b64 + '" alt="' + esc(sage.name) + '" class="sage-avatar-mini">'

        : '<div class="sage-avatar-fallback">' + esc(sage.name.slice(0, 1)) + '</div>';



      quoteHtml = '<div class="classic-quote-box">'

        + '<div class="sage-badge-header">'

        +   avatarImg

        +   '<div class="sage-badge-info">'

        +     '<div class="sage-badge-name">' + esc(sage.title) + '<span class="sage-badge-era">' + esc(sage.era) + '</span></div>'

        +     '<div class="sage-badge-motto">' + esc(sage.motto) + '</div>'

        +   '</div>'

        + '</div>'

        + '<div class="classic-quote-text serif">「' + esc(c.quote) + '」</div>'

        + '<div class="classic-meta-row">'

        + '<span>出处：《' + esc(c.book) + '》' + (c.chapter && c.chapter !== '—' ? ' · ' + esc(c.chapter) : '') + '</span>'

        + '<span>编号：' + esc(c.source_id) + '</span>'

        + '<span class="badge ' + b.cls + '">' + b.text + '</span>'

        + '<button class="collapse-trigger" id="btnToggleClassicDetail">查看考据出处说明</button>'

        + '</div>'

        + '<div class="classic-collapse-detail hidden" id="classicDetailBox">'

        + (cObj ? '<strong>朝代作者：</strong>' + esc(cObj.era_author || '—') + '<br>'

                + '<strong>白话转释：</strong>' + esc(cObj.translation || '—') + '<br>'

                + '<strong>权威版本：</strong>' + esc(cObj.edition || '通行本') + '<br>'

                + '<strong>考据说明：</strong>' + esc(cObj.note || '出处严谨核实，符合引用规范。')

                : '出处核验详单')

        + '</div>'

        + '</div>';

    } else {

      quoteHtml = '<div style="padding:14px;background:var(--color-surface-subtle);border-radius:8px;font-size:13.5px;color:var(--color-muted);margin:10px 0;">'

        + '知识库中暂未找到足够严密对应的古籍字句。不编造、不生搬硬套，是悟堂对待智慧的基本敬畏。'

        + '</div>';

    }



    var stepsHtml = r.micro_action.steps.map(function(s) {

      return '<li>' + esc(s) + '</li>';

    }).join('');



    var html = ''

      + '<!-- 01 听见了 -->'

      + '<div class="step-item">'

      + '  <div class="step-num-col"><div class="step-num-badge">01</div></div>'

      + '  <div class="step-content-col">'

      + '    <div class="step-title">听见了</div>'

      + '    <div class="step-text" id="stepText01">' + esc(r.empathy) + '</div>'

      + '  </div>'

      + '</div>'



      + '<!-- 02 古人有云 -->'

      + '<div class="step-item">'

      + '  <div class="step-num-col"><div class="step-num-badge">02</div></div>'

      + '  <div class="step-content-col">'

      + '    <div class="step-title">古人有云</div>'

      +      quoteHtml

      + '    <div class="step-text" id="stepText02"><strong>现代启发：</strong>' + esc(r.modern_interp) + '</div>'

      + '  </div>'

      + '</div>'



      + '<!-- 03 试试这一招 -->'

      + '<div class="step-item">'

      + '  <div class="step-num-col"><div class="step-num-badge">03</div></div>'

      + '  <div class="step-content-col">'

      + '    <div class="step-title">试试这一招</div>'

      + '    <div class="action-headline" id="stepHeadline03">' + esc(r.micro_action.headline) + '</div>'

      + '    <ol class="action-steps-ol" id="stepOl03">' + stepsHtml + '</ol>'

      + '    <button class="willing-btn' + (appState.willingChecked ? ' checked' : '') + '" id="btnWillingTry">'

      + (appState.willingChecked ? '✓ 已记下，今晚先试这一小步' : '我愿意试一试')

      + '    </button>'

      + '  </div>'

      + '</div>'



      + '<!-- 04 读这一段 -->'

      + '<div class="step-item">'

      + '  <div class="step-num-col"><div class="step-num-badge">04</div></div>'

      + '  <div class="step-content-col">'

      + '    <div class="step-title">读这一段</div>'

      + '    <div class="step-text" id="stepText04">' + esc(r.further_reading) + '</div>'

      + '    <div style="font-size:12.5px;color:var(--color-muted);background:var(--color-bg);padding:8px 12px;border-radius:6px;border:1px solid var(--color-border);margin-top:8px;">'

      + esc(r.safety_note)

      + '    </div>'

      + '  </div>'

      + '</div>';



    $('fourStepList').innerHTML = html;



    // 绑定展开出处

    var trigger = $('btnToggleClassicDetail');

    if (trigger) {

      trigger.onclick = function() {

        var box = $('classicDetailBox');

        if (box.classList.contains('hidden')) {

          box.classList.remove('hidden');

          trigger.textContent = '收起出处考据';

        } else {

          box.classList.add('hidden');

          trigger.textContent = '查看考据出处说明';

        }

      };

    }



    // 绑定「我愿意试一试」

    var willingBtn = $('btnWillingTry');

    if (willingBtn) {

      willingBtn.onclick = function() {

        appState.willingChecked = !appState.willingChecked;

        renderReliefCards(appState.currentCards);

        renderFourStepList(appState.currentResult);

        if (appState.willingChecked) {

          showToast('愿这一步，为你带去一点轻盈与力量');

        }

      };

    }

  }



  function renderResultView(r) {

    $('resultThemeBadge').textContent = '情绪主题：' + r.theme_title;

    renderReliefCards(appState.currentCards);

    renderFourStepList(r);



    // 3D 翻牌展开动效 (Sequential Reveal)

    var mCard = $('resCardMindset');

    var wCard = $('resCardWisdom');

    var aCard = $('resCardAction');

    if (mCard) mCard.classList.remove('is-flipped');

    if (wCard) wCard.classList.remove('is-flipped');

    if (aCard) aCard.classList.remove('is-flipped');



    setTimeout(function() { if (mCard) mCard.classList.add('is-flipped'); }, 200);

    setTimeout(function() { if (wCard) wCard.classList.add('is-flipped'); }, 600);

    setTimeout(function() { if (aCard) aCard.classList.add('is-flipped'); }, 1000);

  }



  // ================= 渲染安全支持页面 (U-04) =================

  var SAFETY_HTML_HIGH =

    '<p style="font-size:15.5px;color:var(--color-ink-light);margin-bottom:12px;">'

  + '通过你的这段文字，我能感受到你此刻可能正承受着巨大的压力与痛苦。请相信，你的难过是真实的，但也请先确认此时此刻的自身安全：'

  + '</p>'

  + '<ol class="safety-steps">'

  + '<li><strong>请先停下眼前的动作：</strong> 如果此时周围有任何可能伤害到自己的物品或环境，请先移动到安全、舒适的地方。</li>'

  + '<li><strong>找一个真人陪陪你：</strong> 无论是一通打给信任朋友或家人的电话，还是联系身边的同事，有人陪伴比独自扛着好很多。</li>'

  + '<li><strong>随时寻求专业援助：</strong> 下方列出了全国 24 小时免费心理危机与援助热线，专业咨询师随时会以温暖接纳的态度倾听你。</li>'

  + '</ol>'

  + '<p style="color:var(--color-muted);font-size:13px;">'

  + '* 本页面已自动阻断常规文化解答与卡片生成。悟堂严格恪守安全边界，不以轻率分析替代危机求助。'

  + '</p>';



  var SAFETY_HTML_REVIEW =

    '<p style="font-size:15.5px;color:var(--color-ink-light);margin-bottom:12px;">'

  + '悟堂是一个陪伴你整理日常情绪与文化启发的小工具，<strong>不提供临床医学诊断、精神科处方、宗教法门指导或运势算命</strong>。'

  + '</p>'

  + '<p style="font-size:14.5px;color:var(--color-ink-light);">'

  + '如果你的困扰涉及具体的医疗确诊、用药调整、法律维权或未成年人保护，请务必咨询具有正规资质的专业机构与医师，我们不适宜为此给出判断。'

  + '</p>'

  + '<p style="font-size:14.5px;color:var(--color-ink-light);">'

  + '如果你只是想梳理当下的情绪起伏，你可以换一种表达，只说说你此刻心里有什么具体的纠结，悟堂依然会真诚地陪你理一理。'

  + '</p>';



  // ================= 东方解忧笺生成与超清 Canvas 绘制 (U-05 / PRD 2.0 F-06) =================

  function applyBookmarkToDom(bmId) {

    appState.selectedBookmark = bmId;

    var jian = $('jianDom');

    if (jian) {

      jian.style.backgroundImage = 'url(' + getBookmarkAsset(bmId) + ')';

      jian.style.backgroundSize = '100% 100%';

      jian.style.backgroundRepeat = 'no-repeat';

    }

    Array.prototype.forEach.call(document.querySelectorAll('.bm-pill'), function(p) {

      if (p.getAttribute('data-bmid') === bmId) {

        p.classList.add('active');

      } else {

        p.classList.remove('active');

      }

    });

  }



  function prepareCardData(r) {

    var isPub = appState.cardPublicVersion;

    var c = r.classic;

    var q = c.quote || '先把心放慢半拍，眼前的结自会松开。';

    var src = c.book ? ('《' + c.book + '》' + (c.chapter && c.chapter !== '—' ? ' · ' + c.chapter : '')) : '悟堂解忧引言';

    var exp = r.modern_interp;

    var act = r.micro_action.headline.replace(/^今晚\s*5\s*分钟[：:]\s*/, '') + '。' + (r.micro_action.steps[0] || '');

    var theme = isPub ? (r.theme_title + ' · 共读精选') : r.theme_title;



    var sage = getSageInfo(r.classic_obj ? r.classic_obj.era_author : '', c.book);

    var avatarEl = $('cardSageAvatar');

    if (avatarEl) {

      if (sage && sage.b64) {

        avatarEl.src = sage.b64;

        avatarEl.style.display = 'inline-block';

      } else {

        avatarEl.style.display = 'none';

      }

    }



    applyBookmarkToDom(appState.selectedBookmark || 'bm_gold_fleck');



    $('cardTheme').textContent = theme;

    $('cardQuote').textContent = '「' + q + '」';

    $('cardSource').textContent = src;

    $('cardExp').textContent = exp;

    if ($('cardActionTag')) {

      $('cardActionTag').textContent = isPub ? '东方智慧微行动（共读推荐）' : '今晚 5 分钟微行动';

    }

    $('cardAction').textContent = act;



    return {

      theme: theme,

      quote: '「' + q + '」',

      src: src,

      exp: exp,

      act: act,

      sage: sage,

      isPublic: isPub,

      slogan: isPub

        ? '让古老智慧，用今天的人听得懂的方式活着 ｜ 严格脱敏 · 东方共读'

        : '让古老智慧，用今天的人听得懂的方式活着'

    };

  }



  function drawRetinaCard(cd) {

    // 东方解忧笺 WYSIWYG 高清所见即所得导出 (1050 x 2250 px, 严格按 2.763 倍对齐屏幕 380x814 卡片字号与排版)

    var W = 1050, H = 2250;

    var k = W / 380; // 约 2.763 倍屏幕高清缩放系数

    var cv = document.createElement('canvas');

    cv.width = W; cv.height = H;

    var g = cv.getContext('2d');



    // 1. 背景宣纸底色

    g.fillStyle = '#FCF9F2';

    g.fillRect(0, 0, W, H);



    // 2. 绘制书笺纹样底图

    var bmKey = appState.selectedBookmark || 'bm_gold_fleck';

    var bmSrc = getBookmarkAsset(bmKey);

    var bgDrawn = false;

    if (bmSrc) {

      var bgImg = new Image();

      bgImg.src = bmSrc;

      if (bgImg.complete && bgImg.naturalWidth > 0) {

        g.drawImage(bgImg, 0, 0, W, H);

        bgDrawn = true;

      }

    }



    if (!bgDrawn) {

      // 降级双框

      g.strokeStyle = '#D6CAB8';

      g.lineWidth = 4;

      g.strokeRect(30, 30, W - 60, H - 60);

      g.strokeStyle = '#E6DCCD';

      g.lineWidth = 2;

      g.strokeRect(45, 45, W - 90, H - 90);



      // 降级印章与品牌名

      var cxFall = W / 2, yFall = 180;

      g.textAlign = 'center';

      g.textBaseline = 'alphabetic';

      g.fillStyle = '#8F2928';

      g.fillRect(cxFall - 160, yFall - 36, 42, 42);

      g.fillStyle = '#FFFFFF';

      g.font = 'bold 24px "Songti SC", "SimSun", serif';

      g.fillText('悟', cxFall - 139, yFall - 6);

      g.fillStyle = '#8F2928';

      g.font = '600 24px "PingFang SC", "Microsoft YaHei", sans-serif';

      g.fillText('悟 堂 · 东 方 解 忧 笺', cxFall + 20, yFall - 6);

    }



    var cx = W / 2;

    var contentW = Math.round(328 * k); // 约 906px，与屏幕中两侧留白保持完全一致

    var leftX = Math.round((W - contentW) / 2); // 约 72px



    // 折行工具函数

    function wrapLines(text, font, maxW) {

      g.font = font;

      var lines = [], line = '';

      for (var i = 0; i < text.length; i++) {

        var ch = text[i];

        var test = line + ch;

        if (g.measureText(test).width > maxW && line) {

          lines.push(line);

          line = ch;

        } else {

          line = test;

        }

      }

      if (line) lines.push(line);

      return lines;

    }



    function roundRect(ctx, x, y, w, h, r) {

      if (w < 2 * r) r = w / 2;

      if (h < 2 * r) r = h / 2;

      ctx.beginPath();

      ctx.moveTo(x + r, y);

      ctx.arcTo(x + w, y, x + w, y + h, r);

      ctx.arcTo(x + w, y + h, x, y + h, r);

      ctx.arcTo(x, y + h, x, y, r);

      ctx.arcTo(x, y, x + w, y, r);

      ctx.closePath();

    }



    // 3. 经典引言（大字宋体，字号 22px * k ≈ 61px，居中对齐）

    var quoteFontSize = Math.round(22 * k); // 61px

    var quoteLineH = Math.round(39.6 * k);   // 109px

    var quoteFont = '600 ' + quoteFontSize + 'px "Songti SC", "SimSun", "STSong", serif';

    var qLines = wrapLines(cd.quote, quoteFont, contentW);



    // 起笔位置严格对应屏幕上的 clamp(145px, 42%, 165px)

    var y = Math.round(155 * k); // 约 428px

    g.textAlign = 'center';

    g.textBaseline = 'alphabetic';

    g.fillStyle = '#262421';

    g.font = quoteFont;

    qLines.forEach(function(l) {

      g.fillText(l, cx, y);

      y += quoteLineH;

    });



    // 4. 出处来源（字号 13px * k ≈ 36px）

    y += Math.round(14 * k);

    var srcFontSize = Math.round(13 * k); // 36px

    var srcFont = srcFontSize + 'px "Songti SC", "SimSun", "STSong", serif';

    g.font = srcFont;

    g.fillStyle = '#77736D';



    var sageImgDrawn = false;

    var sageSize = Math.round(22 * k); // 60px

    if (cd.sage && cd.sage.b64) {

      var sImg = new Image();

      sImg.src = cd.sage.b64;

      if (sImg.complete && sImg.naturalWidth > 0) {

        var srcTextW = g.measureText(cd.src).width;

        var totalSrcW = sageSize + 12 + srcTextW;

        var startX = cx - totalSrcW / 2;

        g.drawImage(sImg, startX, y - sageSize + 6, sageSize, sageSize);

        g.textAlign = 'left';

        g.fillText(cd.src, startX + sageSize + 12, y);

        sageImgDrawn = true;

      }

    }

    if (!sageImgDrawn) {

      g.textAlign = 'center';

      g.fillText(cd.src, cx, y);

    }



    // 5. 分割细线

    y += Math.round(20 * k);

    var lineHalfW = Math.round(22 * k); // 61px

    g.strokeStyle = '#D6CAB8';

    g.lineWidth = Math.round(1.2 * k);

    g.beginPath();

    g.moveTo(cx - lineHalfW, y);

    g.lineTo(cx + lineHalfW, y);

    g.stroke();



    // 6. 现代温润解义（字号 14px * k ≈ 39px，行高 1.85 * 39 ≈ 72px，左对齐）

    y += Math.round(26 * k);

    var expFontSize = Math.round(14 * k); // 39px

    var expLineH = Math.round(26 * k);    // 72px

    var expFont = expFontSize + 'px "PingFang SC", "Microsoft YaHei", sans-serif';

    var expLines = wrapLines(cd.exp, expFont, contentW);

    g.textAlign = 'left';

    g.fillStyle = '#4A443E';

    g.font = expFont;

    expLines.forEach(function(l) {

      g.fillText(l, leftX, y);

      y += expLineH;

    });



    // 7. 今晚 5 分钟微行动卡盒（字号与比例完全对齐屏幕）

    y += Math.round(18 * k);

    var boxPadX = Math.round(16 * k); // 44px

    var boxPadY = Math.round(14 * k); // 39px

    var actTagFontSize = Math.round(12 * k); // 33px

    var actTextFontSize = Math.round(13.5 * k); // 37px

    var actTextLineH = Math.round(23 * k); // 64px

    var actTextFont = actTextFontSize + 'px "PingFang SC", "Microsoft YaHei", sans-serif';



    var innerBoxW = contentW - boxPadX * 2;

    var actLines = wrapLines(cd.act, actTextFont, innerBoxW);

    var boxH = boxPadY * 2 + actTagFontSize + 14 + actLines.length * actTextLineH;



    // 白色卡盒底色与轻柔边线

    g.fillStyle = '#FFFFFF';

    roundRect(g, leftX, y, contentW, boxH, Math.round(8 * k));

    g.fill();

    g.strokeStyle = '#E6DFD4';

    g.lineWidth = Math.round(1.2 * k);

    g.stroke();



    // 行动标题

    g.fillStyle = '#8F2928';

    g.font = '600 ' + actTagFontSize + 'px "PingFang SC", "Microsoft YaHei", sans-serif';

    var actBoxTitle = cd.isPublic ? '东 方 智 慧 微 行 动 （共 读 推 荐）' : '今 晚 5 分 钟 微 行 动';

    g.fillText(actBoxTitle, leftX + boxPadX, y + boxPadY + actTagFontSize - 2);



    // 行动正文

    g.fillStyle = '#262421';

    g.font = actTextFont;

    var textStartY = y + boxPadY + actTagFontSize + 16 + actTextFontSize;

    actLines.forEach(function(l) {

      g.fillText(l, leftX + boxPadX, textStartY);

      textStartY += actTextLineH;

    });



    // 8. 页脚 Slogan（如果未绘制底图，或为公开分享版，才补充落款）

    if (!bgDrawn || cd.isPublic) {

      g.textAlign = 'center';

      g.fillStyle = '#77736D';

      g.font = Math.round(12.5 * k) + 'px "PingFang SC", "Microsoft YaHei", sans-serif';

      g.fillText(cd.slogan, cx, H - Math.round(36 * k));

    }



    return cv.toDataURL('image/png');

  }



  // ================= 视图流转导航控制 =================

  function switchClientView(viewId) {

    appState.clientView = viewId;

    ['userHome', 'userLoading', 'userResult', 'userSafety', 'userCard'].forEach(function(id) {

      var node = $(id);

      if (node) {

        if (id === viewId) node.classList.remove('hidden');

        else node.classList.add('hidden');

      }

    });



    if (viewId === 'userLoading') {

      lotusEngine.start();

    } else {

      lotusEngine.stop();

    }



    window.scrollTo({ top: 0, behavior: 'smooth' });

  }



  function switchMainTab(tab) {

    appState.mainTab = tab;

    var clientArea = $('clientArea');

    var growthArea = $('growthArea');

    var wellbeingArea = $('wellbeingArea');

    var practiceArea = $('practiceArea');

    var cardsArea = $('cardsArea');

    var mineArea = $('mineArea');

    var studioArea = $('studioArea');



    var tabs = ['tabRelief', 'tabGrowth', 'tabWellbeing', 'tabPractice', 'tabCards', 'tabMine', 'tabStudio'];

    tabs.forEach(function(tId) {

      var btn = $(tId);

      if (btn) btn.classList.remove('active');

    });



    [clientArea, growthArea, wellbeingArea, practiceArea, cardsArea, mineArea, studioArea].forEach(function(area) {

      if (area) area.classList.add('hidden');

    });



    if (tab === 'relief') {

      if (clientArea) clientArea.classList.remove('hidden');

      if ($('tabRelief')) $('tabRelief').classList.add('active');

    } else if (tab === 'growth') {

      if (growthArea) growthArea.classList.remove('hidden');

      if ($('tabGrowth')) $('tabGrowth').classList.add('active');

      renderGrowthSection();

    } else if (tab === 'wellbeing') {

      if (wellbeingArea) wellbeingArea.classList.remove('hidden');

      if ($('tabWellbeing')) $('tabWellbeing').classList.add('active');

      renderWellbeingSection();

    } else if (tab === 'practice') {

      if (practiceArea) practiceArea.classList.remove('hidden');

      if ($('tabPractice')) $('tabPractice').classList.add('active');

      renderPracticeSection();

    } else if (tab === 'cards') {

      if (cardsArea) cardsArea.classList.remove('hidden');

      if ($('tabCards')) $('tabCards').classList.add('active');

      renderCardsSection();

    } else if (tab === 'mine') {

      if (mineArea) mineArea.classList.remove('hidden');

      if ($('tabMine')) $('tabMine').classList.add('active');

      renderMineSection();

    } else if (tab === 'studio') {

      if (!appState.isManagerLoggedIn) {

        showToast('主理人工作台仅供主理人登录后访问，请先在「我的」完成认证');

        switchMainTab('mine');

        return;

      }

      if (studioArea) studioArea.classList.remove('hidden');

      if ($('tabStudio')) $('tabStudio').classList.add('active');

      renderStudioOverview();

    }

    window.scrollTo({ top: 0, behavior: 'smooth' });

  }



  // 兼容别名

  function switchMainMode(mode) {

    switchMainTab(mode === 'studio' ? 'studio' : 'relief');

  }



  // ================= 历史足迹记录中心 (Local History Storage) =================

  function getHistoryList() {

    try {

      var raw = localStorage.getItem('wutang_relief_history');

      if (raw) return JSON.parse(raw);

    } catch (e) {}

    return [];

  }



  function saveConsultationHistory(question, scenario, cards, res) {

    try {

      var list = getHistoryList();

      var m = cards ? (cards.mindset || {}) : {};

      var w = cards ? (cards.wisdom || {}) : {};

      var a = cards ? (cards.action || {}) : {};

      var now = new Date();

      var record = {

        id: 'REC-' + Date.now().toString().slice(-6),

        timestamp: now.toISOString(),

        dateStr: now.getFullYear() + '-' + String(now.getMonth() + 1).padStart(2, '0') + '-' + String(now.getDate()).padStart(2, '0') + ' ' + String(now.getHours()).padStart(2, '0') + ':' + String(now.getMinutes()).padStart(2, '0'),

        question: question || (m.title ? '抽牌心境探索：' + m.title : '日常心事觉察'),

        scenario: scenario || 'general',

        themeTitle: (res && res.theme_title) ? res.theme_title : '东方启发视角',

        cards: {

          mindset: { id: m.card_id || m.id, title: m.title || '心境牌', quote: m.quote || '' },

          wisdom: { id: w.card_id || w.id, title: w.title || '东方智慧牌', quote: (w.classic_source ? w.classic_source.quote : '') || w.quote || '', book: (w.classic_source ? w.classic_source.book : '') || '' },

          action: { id: a.card_id || a.id, title: a.title || '微行动牌', headline: (res && res.micro_action ? res.micro_action.headline : '') || (a.title || '') }

        },

        quote: (res && res.classic ? res.classic.quote : '') || (w.classic_source ? w.classic_source.quote : '') || '',

        source: (res && res.classic && res.classic.book) ? ('《' + res.classic.book + '》') : '',

        empathy: (res && res.empathy) ? res.empathy : '',

        modernInterp: (res && res.modern_interp) ? res.modern_interp : '',

        actionHeadline: (res && res.micro_action ? res.micro_action.headline : '') || '',

        actionSteps: (res && res.micro_action ? res.micro_action.steps : []) || [],

        furtherReading: (res && res.further_reading) ? res.further_reading : ''

      };

      list.unshift(record);

      if (list.length > 60) list = list.slice(0, 60);

      localStorage.setItem('wutang_relief_history', JSON.stringify(list));

    } catch (e) {

      console.warn('saveConsultationHistory error:', e);

    }

  }



  function renderMineSection(filterKeyword) {

    updateManagerUI();

    var container = $('historyCardListContainer');

    var notice = $('historyCountNotice');

    if (!container) return;



    var list = getHistoryList();

    if (filterKeyword && filterKeyword.trim()) {

      var kw = filterKeyword.trim().toLowerCase();

      list = list.filter(function(item) {

        return (item.question && item.question.toLowerCase().indexOf(kw) >= 0)

          || (item.cards && item.cards.mindset && item.cards.mindset.title.toLowerCase().indexOf(kw) >= 0)

          || (item.cards && item.cards.wisdom && item.cards.wisdom.title.toLowerCase().indexOf(kw) >= 0)

          || (item.quote && item.quote.toLowerCase().indexOf(kw) >= 0);

      });

    }



    if (notice) {

      notice.textContent = '共已记录 ' + list.length + ' 次心境觉察与解忧探索';

    }



    if (list.length === 0) {

      container.innerHTML = '<div style="padding:40px 20px;text-align:center;color:var(--color-muted);background:var(--color-surface-subtle);border-radius:12px;border:1px dashed var(--color-border);">'

        + '<div style="font-size:32px;margin-bottom:8px;">🍃</div>'

        + '<div style="font-size:14px;color:var(--color-ink-light);margin-bottom:4px;">暂无历史解忧足迹</div>'

        + '<div style="font-size:12.5px;">愿你在心绪纷扰时，随时回来小坐，先把心结整理出头绪。</div>'

        + '</div>';

      return;

    }



    var html = list.map(function(item) {

      var mTitle = item.cards && item.cards.mindset ? item.cards.mindset.title : '心境牌';

      var wTitle = item.cards && item.cards.wisdom ? item.cards.wisdom.title : '智慧牌';

      var aTitle = item.cards && item.cards.action ? item.cards.action.title : '行动牌';

      var q = item.quote ? ('「' + esc(item.quote) + '」' + (item.source ? ' ' + esc(item.source) : '')) : '';



      return '<div class="history-item-card" data-id="' + esc(item.id) + '">'

        + '<div class="history-item-header">'

        + '  <span style="font-weight:600;color:var(--color-primary);">' + esc(item.id) + ' · ' + esc(item.themeTitle || '东方解忧') + '</span>'

        + '  <span>' + esc(item.dateStr) + '</span>'

        + '</div>'

        + '<div class="history-item-question">“' + esc(item.question) + '”</div>'

        + '<div class="history-item-tags">'

        + '  <span class="history-tag mindset">01 当下: ' + esc(mTitle) + '</span>'

        + '  <span class="history-tag wisdom">02 智慧: ' + esc(wTitle) + '</span>'

        + '  <span class="history-tag action">03 行动: ' + esc(aTitle) + '</span>'

        + '</div>'

        + (q ? '<div class="history-item-quote serif">' + q + '</div>' : '')

        + '<div class="history-item-actions">'

        + '  <button class="btn sm" onclick="viewHistoryDetail(\'' + esc(item.id) + '\')">查看四步解忧方</button>'

        + '  <button class="btn sm secondary" onclick="reuseHistoryQuestion(\'' + esc(item.id) + '\')">以此心事重理</button>'

        + '  <button class="btn sm ghost" onclick="deleteHistoryItem(\'' + esc(item.id) + '\')">删除</button>'

        + '</div>'

        + '</div>';

    }).join('');



    container.innerHTML = html;

  }



  window.viewHistoryDetail = function(id) {

    var list = getHistoryList();

    var item = list.find(function(x) { return x.id === id; });

    if (!item) return;



    var body = $('historyDetailBody');

    if (!body) return;



    var mTitle = item.cards && item.cards.mindset ? item.cards.mindset.title : '心境牌';

    var wTitle = item.cards && item.cards.wisdom ? item.cards.wisdom.title : '智慧牌';

    var aTitle = item.cards && item.cards.action ? item.cards.action.title : '行动牌';



    var stepsHtml = (item.actionSteps || []).map(function(s) {

      return '<li style="margin-bottom:4px;">' + esc(s) + '</li>';

    }).join('');



    body.innerHTML = ''

      + '<div style="background:var(--color-surface-subtle);padding:14px;border-radius:10px;margin-bottom:16px;border:1px solid var(--color-border);">'

      + '  <div style="font-size:12px;color:var(--color-muted);margin-bottom:4px;">咨询时间：' + esc(item.dateStr) + ' ｜ 编号：' + esc(item.id) + '</div>'

      + '  <div style="font-size:15.5px;font-weight:600;color:var(--color-ink);line-height:1.5;">“' + esc(item.question) + '”</div>'

      + '</div>'

      + '<div style="display:flex;gap:10px;flex-wrap:wrap;margin-bottom:16px;">'

      + '  <span class="history-tag mindset" style="padding:4px 10px;font-size:12px;">01 当下投影: ' + esc(mTitle) + '</span>'

      + '  <span class="history-tag wisdom" style="padding:4px 10px;font-size:12px;">02 潜意盲区: ' + esc(wTitle) + '</span>'

      + '  <span class="history-tag action" style="padding:4px 10px;font-size:12px;">03 指引路径: ' + esc(aTitle) + '</span>'

      + '</div>'

      + '<div class="four-step-list">'

      + '  <div class="step-item">'

      + '    <div class="step-num-col"><div class="step-num-badge">01</div></div>'

      + '    <div class="step-content-col">'

      + '      <div class="step-title">听见了</div>'

      + '      <div class="step-text">' + esc(item.empathy || '当时的情绪已被温柔接纳。') + '</div>'

      + '    </div>'

      + '  </div>'

      + '  <div class="step-item">'

      + '    <div class="step-num-col"><div class="step-num-badge">02</div></div>'

      + '    <div class="step-content-col">'

      + '      <div class="step-title">古人有云</div>'

      + (item.quote ? '<div class="classic-quote-box"><div class="classic-quote-text serif">「' + esc(item.quote) + '」</div><div class="classic-meta-row"><span>出处：' + esc(item.source || '经典考据') + '</span></div></div>' : '')

      + '      <div class="step-text"><strong>现代视角：</strong>' + esc(item.modernInterp || '换个角度，接纳自己的局限。') + '</div>'

      + '    </div>'

      + '  </div>'

      + '  <div class="step-item">'

      + '    <div class="step-num-col"><div class="step-num-badge">03</div></div>'

      + '    <div class="step-content-col">'

      + '      <div class="step-title">试试这一招</div>'

      + '      <div class="action-headline">' + esc(item.actionHeadline || '今晚微行动') + '</div>'

      + (stepsHtml ? '<ol class="action-steps-ol">' + stepsHtml + '</ol>' : '')

      + '    </div>'

      + '  </div>'

      + '  <div class="step-item">'

      + '    <div class="step-num-col"><div class="step-num-badge">04</div></div>'

      + '    <div class="step-content-col">'

      + '      <div class="step-title">读这一段</div>'

      + '      <div class="step-text">' + esc(item.furtherReading || '经典导读记录。') + '</div>'

      + '    </div>'

      + '  </div>'

      + '</div>';



    $('modalHistoryDetail').classList.add('active');

  };



  window.reuseHistoryQuestion = function(id) {

    var list = getHistoryList();

    var item = list.find(function(x) { return x.id === id; });

    if (!item) return;

    $('userTextarea').value = item.question;

    $('userTextarea').dispatchEvent(new Event('input'));

    switchMainTab('relief');

    switchClientView('userHome');

    showToast('已填入该条历史心事，点击即可重新梳理');

  };



  window.deleteHistoryItem = function(id) {

    var list = getHistoryList().filter(function(x) { return x.id !== id; });

    localStorage.setItem('wutang_relief_history', JSON.stringify(list));

    renderMineSection($('historySearchInput') ? $('historySearchInput').value : '');

    showToast('已删除该条历史足迹');

  };



  window.clearAllHistory = function() {

    if (confirm('确定要清空在此浏览器中保存的所有解忧历史记录吗？')) {

      localStorage.removeItem('wutang_relief_history');

      renderMineSection();

      showToast('历史记录已清空');

    }

  };



  // ================= 账号体系与主理人权限控制 =================

  function authManager(passcodeOrEmail, password) {

    var val = (passcodeOrEmail || '').trim().toLowerCase();

    var pwd = (password || '').trim().toLowerCase();

    var isManagerAccount = (

      val === 'xush09@qq.com' ||

      val === 'admin' ||

      val.indexOf('xush09') !== -1 ||

      val === 'wutang888' ||

      val === 'demo' ||

      val === 'xiaoping' ||

      val === '主理人' ||

      pwd === 'admin' ||

      pwd === 'wutang888'

    );



    if (isManagerAccount) {

      appState.isManagerLoggedIn = true;

      appState.currentUser = null;

      localStorage.setItem('wutang_manager_active', 'true');

      localStorage.removeItem('wutang_current_user');

      updateManagerUI();

      if ($('modalAuth')) $('modalAuth').classList.remove('active');

      showToast('主理人身份已认证！顶栏已自动解锁「主理人工作台」👑');

    } else if (val) {

      // 普通注册用户登录

      appState.isManagerLoggedIn = false;

      appState.currentUser = {

        name: val.split('@')[0],

        account: val,

        role: 'user'

      };

      localStorage.removeItem('wutang_manager_active');

      localStorage.setItem('wutang_current_user', JSON.stringify(appState.currentUser));

      updateManagerUI();

      if ($('modalAuth')) $('modalAuth').classList.remove('active');

      showToast('登录成功，欢迎回来：' + appState.currentUser.name);

    } else {

      showToast('请输入账号或邮箱');

    }

  }



  function registerUser(nickname, account, pwd, confirmPwd) {

    var nick = (nickname || '').trim();

    var acc = (account || '').trim();

    var p = (pwd || '').trim();

    var cp = (confirmPwd || '').trim();



    if (!acc) {

      showToast('请输入常用邮箱或登录账号');

      return;

    }

    if (!p || p.length < 6) {

      showToast('设置密码请至少输入 6 位字符');

      return;

    }

    if (p !== cp) {

      showToast('两次输入的密码不一致，请重新核对');

      return;

    }



    if (acc.toLowerCase().indexOf('xush09') !== -1 || acc.toLowerCase() === 'admin') {

      authManager(acc, p);

      return;

    }



    appState.isManagerLoggedIn = false;

    appState.currentUser = {

      name: nick || acc.split('@')[0],

      account: acc,

      role: 'user'

    };

    localStorage.removeItem('wutang_manager_active');

    localStorage.setItem('wutang_current_user', JSON.stringify(appState.currentUser));

    updateManagerUI();

    if ($('modalAuth')) $('modalAuth').classList.remove('active');

    showToast('注册成功！已开启行者档案，欢迎：' + (nick || acc));

  }



  function logoutUser() {

    appState.currentUser = null;

    localStorage.removeItem('wutang_current_user');

    updateManagerUI();

    showToast('已退出登录，当前处于访客模式');

  }



  function logoutManager() {

    appState.isManagerLoggedIn = false;

    localStorage.removeItem('wutang_manager_active');

    updateManagerUI();

    if (appState.mainTab === 'studio') {

      switchMainTab('relief');

    }

    showToast('已退出主理人身份，工作台已锁定隐藏');

  }



  function updateManagerUI() {

    var tabStudio = $('tabStudio');

    var guestLoginRow = $('guestLoginRow');

    var managerActiveRow = $('managerActiveRow');

    var userActiveRow = $('userActiveRow');

    var mineAvatar = $('mineAvatar');

    var mineUserName = $('mineUserName');

    var mineUserDesc = $('mineUserDesc');



    if (appState.isManagerLoggedIn) {

      // 1. 主理人已登录状态：顶栏自动展示主理人工作台，页面展示主理人身份

      if (tabStudio) {

        tabStudio.classList.remove('hidden');

        tabStudio.style.display = 'inline-flex';

      }

      if (guestLoginRow) guestLoginRow.classList.add('hidden');

      if (userActiveRow) userActiveRow.classList.add('hidden');

      if (managerActiveRow) managerActiveRow.classList.remove('hidden');



      if (mineAvatar) {

        mineAvatar.textContent = '晓';

        mineAvatar.style.background = 'linear-gradient(135deg, #FEF3C7 0%, #FDE68A 100%)';

        mineAvatar.style.color = '#B45309';

        mineAvatar.style.borderColor = '#F59E0B';

      }

      if (mineUserName) {

        mineUserName.innerHTML = '晓萍 · 悟堂主理人 <span class="profile-badge manager">👑 主理人已认证</span>';

      }

      if (mineUserDesc) {

        mineUserDesc.textContent = '账号：xush09@qq.com ｜ 拥有全书典籍检索、来信审核与工业化内容大盘权限';

      }

    } else if (appState.currentUser) {

      // 2. 普通注册用户登录状态

      if (tabStudio) {

        tabStudio.classList.add('hidden');

        tabStudio.style.display = 'none';

      }

      if (guestLoginRow) guestLoginRow.classList.add('hidden');

      if (managerActiveRow) managerActiveRow.classList.add('hidden');

      if (userActiveRow) userActiveRow.classList.remove('hidden');



      var firstChar = (appState.currentUser.name || '行').charAt(0);

      if (mineAvatar) {

        mineAvatar.textContent = firstChar;

        mineAvatar.style.background = 'linear-gradient(135deg, #E0F2FE 0%, #BAE6FD 100%)';

        mineAvatar.style.color = '#0369A1';

        mineAvatar.style.borderColor = '#38BDF8';

      }

      if (mineUserName) {

        mineUserName.innerHTML = esc(appState.currentUser.name) + ' <span class="profile-badge guest" style="background:#E0F2FE;color:#0369A1;border-color:#BAE6FD;">注册行者</span>';

      }

      if (mineUserDesc) {

        mineUserDesc.textContent = '账号：' + esc(appState.currentUser.account) + ' ｜ 解忧足迹与心事已在此设备安全绑定';

      }

    } else {

      // 3. 访客未登录状态：顶栏隐藏主理人工作台，仅保留「登录」按钮

      if (tabStudio) {

        tabStudio.classList.add('hidden');

        tabStudio.style.display = 'none';

      }

      if (guestLoginRow) guestLoginRow.classList.remove('hidden');

      if (managerActiveRow) managerActiveRow.classList.add('hidden');

      if (userActiveRow) userActiveRow.classList.add('hidden');



      if (mineAvatar) {

        mineAvatar.textContent = '悟';

        mineAvatar.style.background = 'linear-gradient(135deg, #FBF4F2 0%, #F5ECE9 100%)';

        mineAvatar.style.color = 'var(--color-primary)';

        mineAvatar.style.borderColor = 'var(--color-primary-border)';

      }

      if (mineUserName) {

        mineUserName.innerHTML = '访客 · 心灵行者 <span class="profile-badge guest">访客模式</span>';

      }

      if (mineUserDesc) {

        mineUserDesc.textContent = '日常心事梳理与解忧记录已保存在此设备本地';

      }

    }

  }



  window.toggleCard3DFlip = function(cardElem) {

    if (!cardElem) return;

    cardElem.classList.toggle('is-flipped');

  };



  function switchStudioTab(viewId) {

    appState.studioView = viewId;

    ['studioOverview', 'studioCards', 'studioNewTask', 'studioPipeline', 'studioReview', 'studioClassics'].forEach(function(id) {

      var n = $(id);

      if (n) {

        if (id === viewId) n.classList.remove('hidden');

        else n.classList.add('hidden');

      }

    });

    Array.prototype.forEach.call(document.querySelectorAll('.studio-nav-btn'), function(btn) {

      if (btn.getAttribute('data-view') === viewId) btn.classList.add('active');

      else btn.classList.remove('active');

    });

    if (viewId === 'studioOverview') renderStudioOverview();

    if (viewId === 'studioCards') renderStudioCards($('studioCardTypeFilter') ? $('studioCardTypeFilter').value : 'all');

    if (viewId === 'studioClassics') renderClassicsList();

    if (viewId === 'studioReview') renderStudioReview(appState.currentDraftKey);

    window.scrollTo({ top: 0, behavior: 'smooth' });

  }



  // 获取当前觉察牌对象 (PRD 2.0 / Option A: 还原为真实成人内心情绪觉察牌)

  function getAwarenessCardObj() {

    if (CARDS_MINDSET && CARDS_MINDSET.length) {

      var idx = Math.abs(appState.awarenessIndex) % CARDS_MINDSET.length;

      return CARDS_MINDSET[idx];

    }

    return { title: '总想让所有人满意', name: '总想让所有人满意', front_text: '我是不是很久没有认真问过自己，真正想要的是什么？', short_description: '自我反思提示卡', question: '最近有没有一件事，你其实不愿意做，却因为担心别人失望而答应了？' };

  }



  function handleClientAwarenessCard() {

    switchMainTab('relief');

    switchClientView('userHome');

    if ($('entryBtnCard')) $('entryBtnCard').click();

  }



  // ================= 觉察牌卡面渲染 (PRD 2.0 F-02: 专注于心境困扰照见) =================

  function renderAwarenessCard(idx) {

    if (!CARDS_MINDSET || !CARDS_MINDSET.length) return;

    var i = Math.abs(idx) % CARDS_MINDSET.length;

    var card = CARDS_MINDSET[i];

    var qText = card.front_text || card.quote || '';

    if ($('awFrontTitle')) $('awFrontTitle').textContent = card.title || '';

    if ($('awFrontQuestion')) $('awFrontQuestion').textContent = qText ? ('「' + qText + '」') : '';

    if ($('awFrontDesc')) $('awFrontDesc').textContent = card.short_description || card.sample_prompt || card.subtitle || '这是一张用于自我反思的提示卡，不代表对你的判断。';

    if ($('awFollowupText')) {

      $('awFollowupText').textContent = card.follow_up_question || card.sample_prompt || '最近有没有一件事，让你产生了类似的心情？写下一两句话…';

    }

    var cardBox = $('awarenessCardBox');

    if (cardBox) {

      if (typeof updateAwarenessFlipUI === 'function') updateAwarenessFlipUI(false);

      else cardBox.classList.remove('is-flipped');

      var frontEl = cardBox.querySelector('.awareness-card-front');

      if (frontEl) {

        var imgSrc = card.image_png || ('assets/cards/mindset/' + (card.card_id || 'M-001') + '.png');

        frontEl.style.backgroundImage = 'url(' + imgSrc + ')';

        frontEl.style.backgroundSize = 'cover';

        frontEl.style.backgroundPosition = 'center';

        frontEl.style.border = 'none';

      }

    }

    if ($('awFollowupBox')) $('awFollowupBox').classList.add('hidden');

    if ($('awProceedWrap')) $('awProceedWrap').classList.add('hidden');

    appState.awarenessFlipped = false;

  }



  // ================= 主理人端：解忧卡牌库渲染 (PRD 2.0) =================

  function renderStudioCards(typeFilter) {

    typeFilter = typeFilter || 'all';

    var container = $('studioCardListContainer');

    if (!container) return;



    var cards = [];

    if (typeFilter === 'all' || typeFilter === 'mindset') {

      CARDS_MINDSET.forEach(function(c) {

        cards.push({

          type: 'mindset',

          typeLabel: '01 心境牌',

          id: c.card_id || c.id,

          title: c.title,

          quote: '「' + (c.front_text || c.quote || '') + '」',

          desc: c.short_description || c.sample_prompt || c.subtitle,

          meta: '标签：' + (c.theme_tags || c.scenarios || []).join('、'),

          statusBadge: '<span class="badge ok">MVP 基础牌</span>'

        });

      });

    }

    if (typeFilter === 'all' || typeFilter === 'wisdom') {

      CARDS_WISDOM.forEach(function(c) {

        var src = c.classic_source || {};

        cards.push({

          type: 'wisdom',

          typeLabel: '02 东方智慧牌',

          id: c.id,

          title: '「' + (src.quote || c.title) + '」',

          quote: '出处：《' + src.book + '》' + (src.chapter && src.chapter !== '—' ? ' · ' + src.chapter : '') + ' (' + src.author + ')',

          desc: c.modern_interpretation,

          meta: '版本：' + (src.edition || '中华书局/通行本') + ' ｜ 考据：' + (src.note || '已核验'),

          statusBadge: '<span class="badge ok">严谨核验</span>'

        });

      });

    }

    if (typeFilter === 'all' || typeFilter === 'action') {

      CARDS_ACTION.forEach(function(c) {

        cards.push({

          type: 'action',

          typeLabel: '03 行动牌',

          id: c.id,

          title: c.title,

          quote: '耗时：约 ' + c.time_estimate_min + ' 分钟 ｜ 阻力：' + c.friction_level,

          desc: (c.steps || []).join('；'),

          meta: '备选：' + ((c.alternatives && c.alternatives[0]) ? c.alternatives[0] : '静心深呼吸') + ' ｜ 场景：' + (c.scenarios || []).join('、'),

          statusBadge: '<span class="badge ok">微步落地</span>'

        });

      });

    }



    if ($('studioCardsSubtitle')) {

      $('studioCardsSubtitle').textContent = '共 ' + (CARDS_MINDSET.length + CARDS_WISDOM.length + CARDS_ACTION.length)

        + ' 张卡牌 · 心境 ' + CARDS_MINDSET.length + ' / 智慧 ' + CARDS_WISDOM.length + ' / 行动 ' + CARDS_ACTION.length + '（显示 ' + cards.length + ' 张）';

    }



    if (!cards.length) {

      container.innerHTML = '<div style="padding:40px;text-align:center;color:var(--color-muted);grid-column:1/-1;">暂无匹配卡牌。</div>';

      return;

    }



    container.innerHTML = cards.map(function(c) {

      return '<div class="studio-card-cell ' + c.type + '">'

        + '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">'

        + '  <span style="font-size:12px;font-weight:700;color:var(--color-primary);">' + esc(c.typeLabel) + ' ｜ ' + esc(c.id) + '</span>'

        +    c.statusBadge

        + '</div>'

        + '<div class="serif" style="font-size:16px;font-weight:600;color:var(--color-ink);margin-bottom:6px;">' + esc(c.title) + '</div>'

        + '<div style="font-size:13px;color:var(--color-gold);margin-bottom:8px;font-weight:500;">' + esc(c.quote) + '</div>'

        + '<div style="font-size:13px;color:var(--color-ink-light);line-height:1.6;margin-bottom:8px;">' + esc(c.desc) + '</div>'

        + '<div style="font-size:11.5px;color:var(--color-muted);background:var(--color-bg);padding:4px 8px;border-radius:4px;border:1px solid var(--color-border);">'

        + esc(c.meta)

        + '</div>'

        + '</div>';

    }).join('');

  }



  // ================= AI 后台与离线解忧联动 (PRD 2.0 AI 驱动) =================

  function runOfflineRelief(caseId, sc, text, presetMindsetCard) {

    var cards = matchReliefCards(sc, text, presetMindsetCard);

    appState.currentCards = cards;

    var res = assembleFourStep(caseId, sc, text, cards);

    appState.currentResult = res;

    renderResultView(res);

    saveConsultationHistory(text, sc, cards, res);

    switchClientView('userResult');

    var w = cards.wisdom || {};
    var ws = w.classic_source || {};
    var masterName = (appState.selectedMaster === 'laozi') ? '老子' : ((appState.selectedMaster === 'shakyamuni') ? '释迦牟尼' : ((appState.selectedMaster === 'all') ? '三圣合参' : '孔子'));
    var fallbackSig = {
      card_name: (w.name || (appState.selectedTrack === 'daoism' ? '若水' : (appState.selectedTrack === 'buddhism' ? '无住' : '克己'))).slice(0, 2),
      master: masterName,
      school: appState.selectedTrack || 'confucianism',
      aphorism: ws.quote || w.original_text || '君子求诸己，万般皆因行未至。',
      english_mantra: (appState.selectedTrack === 'daoism' ? 'Flow like water, rest in quiet simplicity.' : (appState.selectedTrack === 'buddhism' ? 'Abide nowhere to discover true peace.' : 'Self-discipline brings enduring dignity.')),
      classic_source: ws.book ? ('《' + ws.book + '·' + ws.chapter + '》（' + ws.author + '）') : '《论语·卫灵公》（春秋·孔子）',
      quote: ws.quote || '君子求诸己，小人求诸人。',
      interpretation: ws.translation || w.modern_interpretation || '把力气收回到自己身上，是瓦解内耗的唯一解药。',
      action_title: (cards.action && cards.action.title) ? cards.action.title : '静坐调息，记录眼前可控之事',
      action_steps: (cards.action && cards.action.steps) ? cards.action.steps : ['闭目静坐呼吸三次', '记录当下可控之事']
    };
    updateLiberationCardView(fallbackSig);
  }



  function updateStreamingFourStep(fullMarkdown) {

    var lines = fullMarkdown.split('\n');

    var sec01 = '', sec02 = '', sec03 = '', sec04 = '';

    var current = null;

    for (var i = 0; i < lines.length; i++) {

      var l = lines[i];

      if (l.indexOf('01 听见了') !== -1) { current = '01'; continue; }

      if (l.indexOf('02 古人有云') !== -1) { current = '02'; continue; }

      if (l.indexOf('03 试试这一招') !== -1) { current = '03'; continue; }

      if (l.indexOf('04 读这一段') !== -1) { current = '04'; continue; }

      if (current === '01') sec01 += (l + '\n');

      else if (current === '02') sec02 += (l + '\n');

      else if (current === '03') sec03 += (l + '\n');

      else if (current === '04') sec04 += (l + '\n');

    }

    var el01 = $('stepText01');

    if (el01 && sec01.trim()) {

      el01.textContent = sec01.trim();

      if (appState.currentResult) appState.currentResult.empathy = sec01.trim();

    }

    var el02 = $('stepText02');

    if (el02 && sec02.trim()) {

      el02.innerHTML = '<strong>现代启发：</strong>' + esc(sec02.trim());

      if (appState.currentResult) appState.currentResult.modern_interp = sec02.trim();

    }

    var el04 = $('stepText04');

    if (el04 && sec04.trim()) {

      el04.textContent = sec04.trim();

      if (appState.currentResult) appState.currentResult.further_reading = sec04.trim();

    }

  }



  function checkAiBackendStatus() {

    var btn = $('btnAiStatus');

    if (!btn) return;

    if (typeof window === 'undefined' || typeof window.fetch !== 'function') {

      btn.textContent = '离线引擎模式';

      return;

    }

    fetch('http://localhost:8000/api/health', { method: 'GET' })

      .then(function(r) { return r.json(); })

      .then(function(data) {

        if (data.status === 'healthy') {

          appState.aiConnected = true;

          appState.aiModel = data.model;

          var badgeText = data.llm_configured ? ('AI已就绪 (' + data.model + ')') : 'AI流式已就绪';

          btn.textContent = badgeText;

          btn.style.color = 'var(--color-primary)';

          btn.style.borderColor = 'var(--color-primary)';

        }

      })

      .catch(function() {

        appState.aiConnected = false;

        btn.textContent = '离线引擎模式';

        btn.style.color = 'var(--color-muted)';

      });



    btn.onclick = function() {

      if (appState.aiConnected) {

        showToast('已连接悟堂 AI 后台服务 (' + (appState.aiModel || 'FastAPI') + ')，支持 SSE 流式解忧');

      } else {

        showToast('AI 后台服务未开启，当前运行在纯前端离线规则引擎模式。运行 python backend/app.py 即可启动');

      }

    };

  }



  // ================= 用户端业务流程触发 (Submit / PRD 2.0) =================

  function handleClientSubmit(presetMindsetCard) {

    var text = $('userTextarea').value.trim();

    if (!text && !presetMindsetCard) {

      showToast('请先写下一句心里放不下的事');

      $('userTextarea').focus();

      return;

    }

    if (!text && presetMindsetCard) {

      text = presetMindsetCard.title + '：' + (presetMindsetCard.sample_prompt || presetMindsetCard.quote);

      $('userTextarea').value = text;

      $('userTextarea').dispatchEvent(new Event('input'));

    }



    var risk = evaluateRisk(text);

    var caseId = 'WUTANG-' + new Date().toISOString().slice(0, 10).replace(/-/g, '') + '-' + String(strHash(text) % 1000).padStart(3, '0');

    appState.currentCaseId = caseId;



    if (risk.level === 'high_risk') {

      $('safetyMainTitle').textContent = '你写下的这句话，我看到了，也很在意。';

      $('safetyContentArea').innerHTML = SAFETY_HTML_HIGH;

      switchClientView('userSafety');

      return;

    }

    if (risk.level === 'review') {

      $('safetyMainTitle').textContent = '这件事，悟堂可能需要先守住边界。';

      $('safetyContentArea').innerHTML = SAFETY_HTML_REVIEW;

      switchClientView('userSafety');

      return;

    }



    // 正常困扰：进入 U-02 整理过渡状态（3D 莲花绽放旋转与沉淀）

    switchClientView('userLoading');

    $('lStep1').className = 'loading-step-item active';

    $('lStep2').className = 'loading-step-item';

    $('lStep3').className = 'loading-step-item';

    var lotusStatusNode = $('lotusStatusText');

    if (lotusStatusNode) lotusStatusNode.textContent = '正在倾听心绪，感应潜意识投影…';



    var sc = detectScenario(text, appState.selectedScenario);



    // 荷花动效时长设计：无头回归测试环境(jsdom)缩短为 1.0 秒保证自动化测试，真实环境默认 5.0 秒深沉观照

    var isTestEnv = (typeof navigator !== 'undefined' && navigator.userAgent && navigator.userAgent.indexOf('jsdom') !== -1);

    var minLotusDuration = isTestEnv ? 1000 : 5000;

    var step2Delay = isTestEnv ? 350 : 1600;

    var step3Delay = isTestEnv ? 700 : 3300;

    var stepCompleteDelay = isTestEnv ? 950 : 4600;



    var sTimer1 = setTimeout(function() {

      $('lStep1').className = 'loading-step-item done';

      $('lStep2').className = 'loading-step-item active';

      if (lotusStatusNode) lotusStatusNode.textContent = '正在典籍库中寻觅契合的古人视角…';

    }, step2Delay);



    var sTimer2 = setTimeout(function() {

      $('lStep2').className = 'loading-step-item done';

      $('lStep3').className = 'loading-step-item active';

      if (lotusStatusNode) lotusStatusNode.textContent = '正在为您提炼东方智慧与微行动…';

    }, step3Delay);



    var sTimer3 = setTimeout(function() {

      $('lStep3').className = 'loading-step-item done';

      if (lotusStatusNode) lotusStatusNode.textContent = '东方智慧已凝结，正在翻开解忧牌…';

    }, stepCompleteDelay);



    var isMinTimeElapsed = false;

    var hasSwitchedToResult = false;

    var pendingMeta = null;

    var accumulated = '';

    var isStreamingDone = false;

    var minTimeTimer = null;



    function finishToResult() {

      if (hasSwitchedToResult) return;

      if (!isMinTimeElapsed || !pendingMeta) return;

      hasSwitchedToResult = true;



      appState.selectedScenario = pendingMeta.scenario;

      appState.currentCards = pendingMeta.cards;

      var initialRes = assembleFourStep(caseId, pendingMeta.scenario, text, pendingMeta.cards);

      appState.currentResult = initialRes;

      renderResultView(initialRes);

      saveConsultationHistory(text, pendingMeta.scenario, pendingMeta.cards, initialRes);

      switchClientView('userResult');



      var fList = $('fourStepList');

      if (fList && !$('aiStreamIndicator')) {

        var ind = document.createElement('div');

        ind.id = 'aiStreamIndicator';

        ind.style.cssText = 'display:inline-flex;align-items:center;gap:6px;padding:4px 12px;background:rgba(140,58,43,0.08);color:var(--color-primary);border-radius:20px;font-size:12px;font-weight:600;margin-bottom:12px;';

        ind.innerHTML = isStreamingDone ? '悟堂 AI · 东方智慧已倾注完毕' : '悟堂 AI · 流式解忧倾注中…';

        fList.parentNode.insertBefore(ind, fList);

      }

      if (accumulated) {

        updateStreamingFourStep(accumulated);

      }

    }



    minTimeTimer = setTimeout(function() {

      isMinTimeElapsed = true;

      finishToResult();

    }, minLotusDuration);



    // 绑定「延长静观」与「提前揭晓」按钮交互

    var btnExtend = $('btnExtendLotus');

    var btnSkip = $('btnSkipLotus');

    if (btnExtend) {

      btnExtend.onclick = function() {

        clearTimeout(minTimeTimer);

        isMinTimeElapsed = false;

        if (lotusStatusNode) lotusStatusNode.textContent = '已为您延长静观沉淀片刻，请随荷花深呼吸…';

        showToast('已为您延长 5 秒观照时间');

        minTimeTimer = setTimeout(function() {

          isMinTimeElapsed = true;

          finishToResult();

        }, 5000);

      };

    }

    if (btnSkip) {

      btnSkip.onclick = function() {

        if (pendingMeta) {

          isMinTimeElapsed = true;

          finishToResult();

        } else {

          showToast('解忧方正在全力凝聚中，请稍候片刻…');

        }

      };

    }



    function fallbackOffline() {

      clearTimeout(timer);

      setTimeout(function() {

        if (hasSwitchedToResult) return;

        hasSwitchedToResult = true;

        $('lStep1').className = 'loading-step-item done';

        $('lStep2').className = 'loading-step-item done';

        $('lStep3').className = 'loading-step-item done';

        runOfflineRelief(caseId, sc, text, presetMindsetCard);

      }, minLotusDuration);

    }



    if (typeof window === 'undefined' || typeof window.fetch !== 'function') {

      fallbackOffline();

      return;

    }



    var aiEndpoint = 'http://localhost:8000/api/relief/stream';

    var abortCtrl = window.AbortController ? new AbortController() : null;

    var timer = setTimeout(function() { if (abortCtrl) abortCtrl.abort(); }, 30000);



    fetch(aiEndpoint, {

      method: 'POST',

      headers: { 'Content-Type': 'application/json' },

      body: JSON.stringify({
        text: text,
        scenario: sc,
        case_id: caseId,
        track: appState.selectedTrack || 'confucianism',
        master: appState.selectedMaster || 'confucius',
        user_nickname: appState.userNickname || '同修'
      }),

      signal: abortCtrl ? abortCtrl.signal : undefined

    }).then(function(resp) {

      clearTimeout(timer);

      if (!resp.ok || !resp.body) throw new Error('Backend HTTP ' + resp.status);



      var reader = resp.body.getReader();

      var decoder = new TextDecoder('utf-8');

      var buffer = '';



      function read() {

        return reader.read().then(function(chunk) {

          if (chunk.done) {

            isStreamingDone = true;

            var ind = $('aiStreamIndicator');

            if (ind) ind.innerHTML = '悟堂 AI · 东方智慧已倾注完毕';

            return;

          }

          buffer += decoder.decode(chunk.value, { stream: true });

          var parts = buffer.split('\n\n');

          buffer = parts.pop();



          for (var i = 0; i < parts.length; i++) {

            var p = parts[i].trim();

            if (p.startsWith('data: ')) {

              try {

                var evt = JSON.parse(p.slice(6));

                if (evt.type === 'safety') {

                  clearTimeout(minTimeTimer);

                  clearTimeout(sTimer1);

                  clearTimeout(sTimer2);

                  clearTimeout(sTimer3);

                  $('safetyMainTitle').textContent = '你写下的这句话，我看到了，也很在意。';

                  $('safetyContentArea').innerHTML = '<div style="white-space:pre-wrap;line-height:1.7;">' + esc(evt.message) + '</div>';

                  switchClientView('userSafety');

                  return;

                } else if (evt.type === 'meta') {

                  pendingMeta = evt;

                  finishToResult();

                } else if (evt.type === 'token') {

                  accumulated += evt.content;

                  if (hasSwitchedToResult) {

                    updateStreamingFourStep(accumulated);

                  }

                } else if (evt.type === 'done') {

                  isStreamingDone = true;

                  var ind = $('aiStreamIndicator');

                  if (ind) ind.innerHTML = '悟堂 AI · 东方智慧已倾注完毕';

                  try {

                    var list = getHistoryList();

                    if (list.length > 0 && appState.currentResult) {

                      list[0].empathy = appState.currentResult.empathy || list[0].empathy;

                      list[0].modernInterp = appState.currentResult.modern_interp || list[0].modernInterp;

                      list[0].furtherReading = appState.currentResult.further_reading || list[0].furtherReading;

                      localStorage.setItem('wutang_relief_history', JSON.stringify(list));

                    }

                  } catch (e) {}

                }

              } catch (err) {}

            }

          }

          return read();

        });

      }

      return read();



    }).catch(function(e) {

      fallbackOffline();

    });

  }



  // ================= 初始化场景标签 =================

  function initScenarioChips() {

    var grid = $('scenarioGrid');

    grid.innerHTML = SCENARIOS.map(function(s) {

      return '<button class="scenario-chip" data-key="' + s.key + '" aria-pressed="false">'

        + '<div class="scenario-chip-header">'

        + '  <span class="chip-title">' + esc(s.label) + '</span>'

        + '  <span class="check-icon">✓</span>'

        + '</div>'

        + '<span class="chip-sub">' + esc(s.sub) + '</span>'

        + '</button>';

    }).join('');



    grid.addEventListener('click', function(e) {

      var btn = e.target.closest('.scenario-chip');

      if (!btn) return;

      var k = btn.getAttribute('data-key');

      var wasPressed = btn.getAttribute('aria-pressed') === 'true';



      Array.prototype.forEach.call(grid.children, function(c) {

        c.setAttribute('aria-pressed', 'false');

      });



      if (wasPressed) {

        appState.selectedScenario = null;

      } else {

        btn.setAttribute('aria-pressed', 'true');

        appState.selectedScenario = k;

      }

    });

  }



  // ================= 主理人端：渲染总览任务流水 (A-01) =================

  var MOCK_TASKS = [

    {

      id: 'WUTANG-SYN-004',

      type: '合成测试用例',

      text: '同事总把活儿推给我，不好意思拒绝，怕他说不合群…',

      scenario: '松绑 · 关系与边界',

      consent: '已授权 (2026-10-16 09:00)',

      citation: 'verified (论语·颜渊)',

      status: '已成文 · 待审核'

    },

    {

      id: 'WUTANG-SYN-007',

      type: '合成测试用例',

      text: '计划了半年的副业建了七八个文档，每次想动手就怕做不好…',

      scenario: '破局 · 行动与自律',

      consent: '已授权 (2026-10-16 09:30)',

      citation: 'needs_review (格言联璧)',

      status: '已成文 · 待审核'

    },

    {

      id: 'WUTANG-SYN-011',

      type: '合成案例 (含PII)',

      text: '我叫李小雨，在杭州一家叫云图的广告公司做设计…',

      scenario: '松绑 · 关系与边界',

      consent: '已授权 (2026-10-16 09:45)',

      citation: 'verified (格言联璧)',

      status: '已成文 · 脱敏待核验'

    },

    {

      id: 'WUTANG-SYN-001',

      type: '合成测试用例',

      text: '领导当着全组的面说我方案不行，回家一直在内耗…',

      scenario: '去班味 · 职场评价',

      consent: '未授权',

      citation: 'verified (论语·卫灵公)',

      status: '仅回应 · 不公开'

    }

  ];



  function renderStudioOverview() {

    var vCount = CLASSICS.filter(function(c) { return c.status === 'verified'; }).length;

    var nfCount = CLASSICS.filter(function(c) { return c.status === 'not_found'; }).length;

    if ($('mVerifiedClassics')) {

      $('mVerifiedClassics').textContent = vCount || 483;

    }

    if ($('mVerifiedClassicsSub')) {

      $('mVerifiedClassicsSub').textContent = '资料库总计 ' + CLASSICS.length + ' 条 · 含 ' + nfCount + ' 条辨伪';

    }



    var tbody = $('taskTableBody');

    tbody.innerHTML = MOCK_TASKS.map(function(t) {

      var badgeCls = t.consent.indexOf('已授权') >= 0 ? 'ok' : 'rev';

      return '<tr>'

        + '<td><strong>' + esc(t.id) + '</strong></td>'

        + '<td>' + esc(t.type) + '</td>'

        + '<td style="max-width:240px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;" title="' + esc(t.text) + '">' + esc(t.text) + '</td>'

        + '<td><span class="badge ' + badgeCls + '">' + esc(t.consent) + '</span></td>'

        + '<td>' + esc(t.citation) + '</td>'

        + '<td><span class="badge ok">' + esc(t.status) + '</span></td>'

        + '<td><button class="btn sm secondary btn-view-pipeline" data-id="' + esc(t.id) + '">查看流转</button></td>'

        + '</tr>';

    }).join('');



    Array.prototype.forEach.call(document.querySelectorAll('.btn-view-pipeline'), function(btn) {

      btn.onclick = function() {

        var tid = btn.getAttribute('data-id');

        openPipelineView(tid);

      };

    });

  }



  // ================= 主理人端：工作流流转详情 (A-03) =================

  var PIPELINE_STEPS = [

    { num: 1, name: '输入校验与风险分流', role: '安全守门人 (严守拙)', time: '12ms', status: 'ok', detail: '评估危机词库与高危句式正则，判定为 normal 安全状态，放行。' },

    { num: 2, name: '用户困扰理解与共情', role: '倾听共情官 (闻心语)', time: '85ms', status: 'ok', detail: '提取情绪关键词与核心困境，生成 2 句不武断、不说教的温和共情。' },

    { num: 3, name: '经典资料检索与匹配', role: '国学考据官 (章有据)', time: '42ms', status: 'ok', detail: '从 500 条人工考据语料中精确匹配契合场景与主题的经典典故。' },

    { num: 4, name: '四步回应结构化生成', role: '解忧流程导演 (常明川)', time: '60ms', status: 'ok', detail: '将听见了、古人有云、微行动、延伸阅读组装为标准四步数据。' },

    { num: 5, name: '经典出处与引文核验', role: '考据组核验员', time: '18ms', status: 'ok', detail: '核验篇章原文、版本注释及来源编号，确认非现代杜撰伪作。' },

    { num: 6, name: '隐私与脱敏检查 (PII)', role: '安全与隐私守门人', time: '35ms', status: 'ok', detail: '对真实姓名、城市、机构、具体日期进行模糊去标识化处理。' },

    { num: 7, name: '东方解忧笺生成', role: '内容主编官 (舒成锦)', time: '22ms', status: 'ok', detail: '脱敏提取主题金句与 5 分钟微行动，生成 4:5 东方古风信笺载体。' },

    { num: 8, name: '公众号文章草稿生成', role: '内容工作流引擎', time: '98ms', status: 'ok', detail: '已核验用户公开共读授权与时间戳，完成草稿沉淀（状态为待主理人审核）。' }

  ];



  function openPipelineView(taskId) {

    appState.currentStudioTask = taskId;

    $('plTaskTitle').textContent = '任务流水监控：' + taskId;

    $('plTaskMeta').textContent = '来源：标准测试集 ｜ 编号：' + taskId + ' ｜ 授权状态：已确认授权';



    var container = $('pipelineStepList');

    container.innerHTML = PIPELINE_STEPS.map(function(s) {

      return '<div class="pipeline-step-card">'

        + '  <div class="step-main-info">'

        + '    <div class="step-badge-idx">' + s.num + '</div>'

        + '    <div>'

        + '      <div class="step-title-text">' + esc(s.name) + '</div>'

        + '      <div class="step-meta-text">负责角色：' + esc(s.role) + ' ｜ 耗时：' + esc(s.time) + '</div>'

        + '    </div>'

        + '  </div>'

        + '  <div style="display:flex;align-items:center;gap:12px;">'

        + '    <span class="badge ok">✓ 已完成</span>'

        + '  </div>'

        + '  <div style="width:100%;font-size:13px;color:var(--color-muted);background:var(--color-surface-subtle);padding:8px 12px;border-radius:6px;border:1px solid var(--color-border);margin-top:6px;">'

        + '    <strong>执行详情：</strong>' + esc(s.detail)

        + '  </div>'

        + '</div>';

    }).join('');



    switchStudioTab('studioPipeline');

  }



  // ================= 主理人端：内容审核与合规清单 (A-04) =================

  function renderStudioReview(draftKey) {

    appState.currentDraftKey = draftKey;

    var draft = ARTICLE_DRAFTS[draftKey];

    var pane = $('articlePreviewPane');



    if (!draft) {

      pane.innerHTML = '<p style="color:var(--color-muted);">未找到指定草稿内容。</p>';

      return;

    }



    // 将 Markdown 简易转为 HTML 预览

    var lines = draft.content.split('\n');

    var html = lines.map(function(line) {

      line = line.trim();

      if (!line) return '<br>';

      if (line.indexOf('# ') === 0) return '<h3>' + esc(line.slice(2)) + '</h3>';

      if (line.indexOf('## ') === 0) return '<h4 style="margin:16px 0 6px;color:var(--color-primary);">' + esc(line.slice(3)) + '</h4>';

      if (line.indexOf('> ') === 0) return '<blockquote>' + esc(line.slice(2)) + '</blockquote>';

      if (line.indexOf('- ') === 0) return '<li style="margin-left:20px;">' + esc(line.slice(2)) + '</li>';

      return '<p style="margin:6px 0;">' + esc(line) + '</p>';

    }).join('');



    pane.innerHTML = html;



    // 显示 PII 去标识化详情

    var piiBox = $('piiReviewBox');

    if (draftKey === 'WUTANG-SYN-011') {

      piiBox.innerHTML = '<span style="color:var(--color-warning);font-weight:600;">[提示] 植入 PII 脱敏核查：</span>'

        + '<br>原文中「李小雨（姓名）」、「杭州云图（单位/地点）」、「3月8号（具体时间）」已由守门人 Skill 成功剔除，'

        + '正文中已替换为泛化的「当事人」与「某地广告公司」，熟人无法借此反推。';

    } else {

      piiBox.innerHTML = '<strong>脱敏与授权：</strong> 该案例已获用户公开共读明确授权（带合法时间戳），未检出高危直接标识。';

    }

  }



  // ================= 主理人端：经典资料库检索与筛选 (A-05) =================

  function renderClassicsList() {

    var kw = $('classicsSearchInput').value.trim().toLowerCase();

    var cat = $('classicsCategoryFilter').value;

    var st = $('classicsStatusFilter').value;



    var filtered = CLASSICS.filter(function(c) {

      if (cat !== 'all' && c.category !== cat) return false;

      if (st !== 'all' && c.status !== st) return false;

      if (kw) {

        var str = (c.quote + ' ' + c.book + ' ' + c.era_author + ' ' + c.themes + ' ' + c.interpretation).toLowerCase();

        if (str.indexOf(kw) < 0) return false;

      }

      return true;

    });



    var container = $('classicsListContainer');

    if ($('classicsSubtitle')) {

      var vCount = CLASSICS.filter(function(c) { return c.status === 'verified'; }).length;

      $('classicsSubtitle').textContent = '共 ' + CLASSICS.length + ' 条经典考据条目 · ' + vCount + ' 条已核验（显示 ' + filtered.length + ' 条）';

    }

    if (!filtered.length) {

      container.innerHTML = '<div style="padding:40px;text-align:center;color:var(--color-muted);">资料库暂无匹配条目。先导入或调整筛选关键词。</div>';

      return;

    }



    container.innerHTML = filtered.map(function(c) {

      var b = BADGE_CONFIG[c.status] || BADGE_CONFIG.not_found;

      var sage = getSageInfo(c.era_author, c.book);

      var avatarImg = sage.b64

        ? '<img src="' + sage.b64 + '" alt="' + esc(sage.name) + '" title="' + esc(sage.title) + '" style="width:30px;height:30px;border-radius:6px;box-shadow:0 1px 3px rgba(0,0,0,0.08);border:1px solid var(--color-border);flex-shrink:0;">'

        : '';



      return '<div class="classics-item-card">'

        + '<div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:8px;gap:10px;">'

        + '  <div style="display:flex;align-items:center;gap:10px;">'

        +      avatarImg

        + '    <div>'

        + '      <strong style="font-size:15px;color:var(--color-primary);">' + esc(c.id) + ' ｜ ' + esc(c.category) + '</strong>'

        + '      <span style="margin-left:8px;font-size:13px;color:var(--color-muted);">《' + esc(c.book) + '》' + (c.chapter && c.chapter !== '—' ? ' · ' + esc(c.chapter) : '') + '</span>'

        + '      <span style="margin-left:6px;font-size:11.5px;color:var(--color-muted);background:var(--color-bg);padding:1px 6px;border-radius:4px;border:1px solid var(--color-border);">' + esc(c.era_author || sage.name) + '</span>'

        + '    </div>'

        + '  </div>'

        + '  <span class="badge ' + b.cls + '">' + b.text + '</span>'

        + '</div>'

        + '<div class="serif" style="font-size:18px;margin:8px 0;color:var(--color-ink);font-weight:600;">「' + esc(c.quote) + '」</div>'

        + '<div style="font-size:13.5px;color:var(--color-ink-light);margin-bottom:6px;"><strong>白话：</strong>' + esc(c.translation) + '</div>'

        + '<div style="font-size:13.5px;color:var(--color-ink-light);margin-bottom:8px;"><strong>视角：</strong>' + esc(c.interpretation) + '</div>'

        + '<div style="font-size:12.5px;color:var(--color-muted);background:var(--color-bg);padding:6px 10px;border-radius:4px;border:1px solid var(--color-border);">'

        + '<strong>版本校注：</strong>' + esc(c.edition || '通行本') + ' ｜ <strong>考据记录：</strong>' + esc(c.note)

        + '</div>'

        + '</div>';

    }).join('');

  }



  // ================= 页面初始化与事件绑定 =================

  function setupEvents() {

    // 1. 顶栏模式切换 (PRD 3.0 全量 6 大用户入口 + 1 个主理人入口)

    if ($('tabRelief')) $('tabRelief').onclick = function() { switchMainTab('relief'); };

    if ($('tabClient')) $('tabClient').onclick = function() { switchMainTab('relief'); };

    if ($('tabGrowth')) $('tabGrowth').onclick = function() { switchMainTab('growth'); };

    if ($('tabWellbeing')) $('tabWellbeing').onclick = function() { switchMainTab('wellbeing'); };

    if ($('tabPractice')) $('tabPractice').onclick = function() { switchMainTab('practice'); };

    if ($('tabCards')) $('tabCards').onclick = function() { switchMainTab('cards'); };

    if ($('tabMine')) $('tabMine').onclick = function() { switchMainTab('mine'); };

    if ($('tabStudio')) $('tabStudio').onclick = function() { switchMainTab('studio'); };

    if ($('headerBrand')) $('headerBrand').onclick = function() { switchMainTab('relief'); switchClientView('userHome'); };



    // 2. 「我的」模块内部事件绑定 (登录/注册弹窗卡牌、主理人权限、退出登录等)

    if ($('btnOpenAuthModal')) {

      $('btnOpenAuthModal').onclick = function() {

        if ($('modalAuth')) {

          $('modalAuth').classList.add('active');

          if ($('authInputAccount')) $('authInputAccount').focus();

        }

      };

    }

    if ($('closeAuthModal')) {

      $('closeAuthModal').onclick = function() {

        if ($('modalAuth')) $('modalAuth').classList.remove('active');

      };

    }

    if ($('tabBtnLogin')) {

      $('tabBtnLogin').onclick = function() {

        if ($('authPanelLogin')) $('authPanelLogin').classList.remove('hidden');

        if ($('authPanelRegister')) $('authPanelRegister').classList.add('hidden');

        $('tabBtnLogin').classList.add('active');

        $('tabBtnLogin').style.background = '#FFF';

        $('tabBtnLogin').style.fontWeight = '600';

        $('tabBtnLogin').style.color = 'var(--color-primary)';

        if ($('tabBtnRegister')) {

          $('tabBtnRegister').classList.remove('active');

          $('tabBtnRegister').style.background = 'transparent';

          $('tabBtnRegister').style.fontWeight = '500';

          $('tabBtnRegister').style.color = 'var(--color-ink-light)';

        }

        if ($('authModalHeaderTitle')) $('authModalHeaderTitle').textContent = '悟堂 · 行者登录';

      };

    }

    if ($('tabBtnRegister')) {

      $('tabBtnRegister').onclick = function() {

        if ($('authPanelRegister')) $('authPanelRegister').classList.remove('hidden');

        if ($('authPanelLogin')) $('authPanelLogin').classList.add('hidden');

        $('tabBtnRegister').classList.add('active');

        $('tabBtnRegister').style.background = '#FFF';

        $('tabBtnRegister').style.fontWeight = '600';

        $('tabBtnRegister').style.color = 'var(--color-primary)';

        if ($('tabBtnLogin')) {

          $('tabBtnLogin').classList.remove('active');

          $('tabBtnLogin').style.background = 'transparent';

          $('tabBtnLogin').style.fontWeight = '500';

          $('tabBtnLogin').style.color = 'var(--color-ink-light)';

        }

        if ($('authModalHeaderTitle')) $('authModalHeaderTitle').textContent = '新行者注册';

      };

    }

    if ($('linkSwitchToReg')) {

      $('linkSwitchToReg').onclick = function() {

        if ($('tabBtnRegister')) $('tabBtnRegister').click();

      };

    }

    if ($('linkSwitchToLogin')) {

      $('linkSwitchToLogin').onclick = function() {

        if ($('tabBtnLogin')) $('tabBtnLogin').click();

      };

    }

    if ($('btnSubmitLoginAction')) {

      $('btnSubmitLoginAction').onclick = function() {

        var acc = $('authInputAccount') ? $('authInputAccount').value : '';

        var pwd = $('authInputPassword') ? $('authInputPassword').value : '';

        authManager(acc, pwd);

      };

    }

    if ($('authInputPassword')) {

      $('authInputPassword').onkeydown = function(e) {

        if (e.key === 'Enter') {

          var acc = $('authInputAccount') ? $('authInputAccount').value : '';

          authManager(acc, this.value);

        }

      };

    }

    if ($('authInputAccount')) {

      $('authInputAccount').onkeydown = function(e) {

        if (e.key === 'Enter') {

          if ($('authInputPassword')) $('authInputPassword').focus();

        }

      };

    }

    if ($('btnQuickDemoLoginAction')) {

      $('btnQuickDemoLoginAction').onclick = function() {

        if ($('authInputAccount')) $('authInputAccount').value = 'xush09@qq.com';

        if ($('authInputPassword')) $('authInputPassword').value = 'admin';

        authManager('xush09@qq.com', 'admin');

      };

    }

    if ($('btnSubmitRegisterAction')) {

      $('btnSubmitRegisterAction').onclick = function() {

        var nick = $('regInputNickname') ? $('regInputNickname').value : '';

        var acc = $('regInputAccount') ? $('regInputAccount').value : '';

        var pwd = $('regInputPassword') ? $('regInputPassword').value : '';

        var cpwd = $('regInputConfirmPassword') ? $('regInputConfirmPassword').value : '';

        registerUser(nick, acc, pwd, cpwd);

      };

    }

    if ($('regInputConfirmPassword')) {

      $('regInputConfirmPassword').onkeydown = function(e) {

        if (e.key === 'Enter') {

          if ($('btnSubmitRegisterAction')) $('btnSubmitRegisterAction').click();

        }

      };

    }

    if ($('btnLogoutUser')) {

      $('btnLogoutUser').onclick = function() {

        logoutUser();

      };

    }

    if ($('btnLogoutManager')) {

      $('btnLogoutManager').onclick = function() {

        logoutManager();

      };

    }

    if ($('btnGoStudioFromMine')) {

      $('btnGoStudioFromMine').onclick = function() {

        switchMainTab('studio');

      };

    }

    if ($('btnReturnToRelief')) {

      $('btnReturnToRelief').onclick = function() {

        switchMainTab('relief');

      };

    }

    if ($('btnLogoutStudio')) {

      $('btnLogoutStudio').onclick = function() {

        logoutManager();

      };

    }



    if ($('btnClearHistoryBtn')) {

      $('btnClearHistoryBtn').onclick = function() {

        clearAllHistory();

      };

    }

    if ($('historySearchInput')) {

      $('historySearchInput').oninput = function() {

        renderMineSection(this.value);

      };

    }

    if ($('btnCloseHistoryDetail')) {

      $('btnCloseHistoryDetail').onclick = function() {

        $('modalHistoryDetail').classList.remove('active');

      };

    }

    if ($('btnCloseHistoryDetailBottom')) {

      $('btnCloseHistoryDetailBottom').onclick = function() {

        $('modalHistoryDetail').classList.remove('active');

      };

    }



    if ($('btnOpenGalleryFromMine')) {

      $('btnOpenGalleryFromMine').onclick = function() {

        $('modalCardGallery').classList.add('active');

        renderCardGallery('all');

      };

    }



    // 3. 模态框打开与关闭 (兼容)

    if ($('btnExplainModal')) $('btnExplainModal').onclick = function() { $('modalExplain').classList.add('active'); };

    if ($('closeExplainModal')) $('closeExplainModal').onclick = function() { $('modalExplain').classList.remove('active'); };

    if ($('btnIUnderstandExplain')) $('btnIUnderstandExplain').onclick = function() { $('modalExplain').classList.remove('active'); };



    if ($('btnPrivacyModal')) $('btnPrivacyModal').onclick = function() { $('modalPrivacy').classList.add('active'); };

    if ($('closePrivacyModal')) $('closePrivacyModal').onclick = function() { $('modalPrivacy').classList.remove('active'); };

    if ($('btnIUnderstandPrivacy')) $('btnIUnderstandPrivacy').onclick = function() { $('modalPrivacy').classList.remove('active'); };



    // 3. 用户端双入口与交互 (PRD 2.0 F-01 & F-02)

    $('entryBtnDirect').onclick = function() {

      appState.entryTab = 'direct';

      $('entryBtnDirect').classList.add('active');

      $('entryBtnCard').classList.remove('active');

      $('entryDirectArea').classList.remove('hidden');

      $('entryCardArea').classList.add('hidden');

    };



    $('entryBtnCard').onclick = function() {

      appState.entryTab = 'card';

      $('entryBtnCard').classList.add('active');

      $('entryBtnDirect').classList.remove('active');

      $('entryDirectArea').classList.add('hidden');

      $('entryCardArea').classList.remove('hidden');

      if (!appState.awarenessFlipped) {

        var total = (CARDS_MINDSET && CARDS_MINDSET.length) ? CARDS_MINDSET.length : 16;

        appState.awarenessIndex = Math.floor(Math.random() * total);

        renderAwarenessCard(appState.awarenessIndex);

      }

    };



    function updateAwarenessFlipUI(isFlipped) {

      appState.awarenessFlipped = !!isFlipped;

      var box = $('awarenessCardBox');

      var wordCard = $('awarenessWordCard');

      if (box) {

        if (isFlipped) box.classList.add('is-flipped');

        else box.classList.remove('is-flipped');

      }

      if (wordCard) {

        if (isFlipped) wordCard.classList.add('is-revealed');

        else wordCard.classList.remove('is-revealed');

      }

    }



    var awarenessCardBox = $('awarenessCardBox');

    if (awarenessCardBox) {

      awarenessCardBox.onclick = function(e) {

        updateAwarenessFlipUI(!appState.awarenessFlipped);

      };

    }



    $('btnAwResonates').onclick = function(e) {

      e.stopPropagation();

      appState.awarenessReaction = 'resonates';

      var card = getAwarenessCardObj();

      var cardTitle = card ? (card.name || card.title) : '当下';

      appState.selectedScenario = (card && card.scenarios && card.scenarios[0]) ? card.scenarios[0] : 'work';

      $('awFollowupBox').classList.remove('hidden');

      $('awProceedWrap').classList.remove('hidden');

      showToast('已确认心境：「' + cardTitle + '」，可直接继续或写句补充');

    };



    $('btnAwPartly').onclick = function(e) {

      e.stopPropagation();

      var card = getAwarenessCardObj();

      var cardTitle = card ? (card.name || card.title) : '当下';

      appState.entryTab = 'direct';

      $('entryBtnDirect').classList.add('active');

      $('entryBtnCard').classList.remove('active');

      $('entryDirectArea').classList.remove('hidden');

      $('entryCardArea').classList.add('hidden');

      $('userTextarea').value = '关于「' + cardTitle + '」，我想说的是：';

      $('userTextarea').dispatchEvent(new Event('input'));

      $('userTextarea').focus();

      showToast('已填入心境，请补充你的具体情况');

    };



    $('btnAwChange').onclick = function(e) {

      e.stopPropagation();

      updateAwarenessFlipUI(false);

      setTimeout(function() {

        var total = (CARDS_MINDSET && CARDS_MINDSET.length) ? CARDS_MINDSET.length : 16;

        var current = appState.awarenessIndex;

        var next = Math.floor(Math.random() * (total - 1));

        if (next >= current) next = (next + 1) % total;

        appState.awarenessIndex = next;

        renderAwarenessCard(appState.awarenessIndex);

        updateAwarenessFlipUI(true);

      }, 240);

    };



    $('btnAwCancel').onclick = function(e) {

      e.stopPropagation();

      appState.entryTab = 'direct';

      $('entryBtnDirect').classList.add('active');

      $('entryBtnCard').classList.remove('active');

      $('entryDirectArea').classList.remove('hidden');

      $('entryCardArea').classList.add('hidden');

    };



    $('btnAwProceed').onclick = function() {

      var card = getAwarenessCardObj();

      var cardTitle = card ? (card.name || card.title) : '当下';

      var note = $('awFollowupInput').value.trim();

      var qText = card ? (card.question || card.front_text || card.quote || card.core || '') : '';

      var text = '【' + cardTitle + '】' + (note ? note : qText);

      $('userTextarea').value = text;

      handleClientSubmit(card);

    };



    var textarea = $('userTextarea');

    var charCount = $('charCount');

    var submitBtn = $('btnSubmitClient');



    textarea.addEventListener('input', function() {

      var len = textarea.value.length;

      charCount.textContent = len + ' / 600';

      if (len >= 600) charCount.classList.add('warn');

      else charCount.classList.remove('warn');



      if (textarea.value.trim().length > 0) {

        submitBtn.removeAttribute('disabled');

      } else {

        submitBtn.setAttribute('disabled', 'true');

      }

    });



    textarea.addEventListener('keydown', function(e) {

      if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {

        if (!submitBtn.disabled) handleClientSubmit();

      }

    });



    submitBtn.onclick = function() { handleClientSubmit(); };



    // 快捷推荐灵感药丸

    Array.prototype.forEach.call(document.querySelectorAll('.inspo-pill'), function(pill) {

      pill.onclick = function() {

        textarea.value = pill.getAttribute('data-inspo');

        textarea.dispatchEvent(new Event('input'));

        textarea.focus();

        showToast('已填入体验案例，点击「帮我理一理」即可梳理');

      };

    });



    // 4. 结果页交互与四步折叠

    var toggleFourStepBtn = $('btnToggleFourStepDetail');

    if (toggleFourStepBtn) {

      toggleFourStepBtn.onclick = function() {

        var list = $('fourStepList');

        if (list.classList.contains('hidden')) {

          list.classList.remove('hidden');

          toggleFourStepBtn.textContent = '收起文字版';

        } else {

          list.classList.add('hidden');

          toggleFourStepBtn.textContent = '查看完整文字版';

        }

      };

    }



    $('btnResetClient').onclick = function() {

      textarea.value = '';

      textarea.dispatchEvent(new Event('input'));

      appState.selectedScenario = null;

      appState.currentResult = null;

      appState.willingChecked = false;

      Array.prototype.forEach.call($('scenarioGrid').children, function(c) {

        c.setAttribute('aria-pressed', 'false');

      });

      switchClientView('userHome');

    };



    $('btnSafetyBack').onclick = function() {

      switchClientView('userHome');

    };



    $('btnCopyResult').onclick = function() {

      if (!appState.currentResult) return;

      var r = appState.currentResult;

      var mdText = '# 悟堂 · 四步解忧方回应\n\n'

        + '## 01 听见了\n' + r.empathy + '\n\n'

        + '## 02 古人有云\n' + (r.classic.quote ? '「' + r.classic.quote + '」——《' + r.classic.book + '》\n现代视角：' + r.modern_interp : r.modern_interp) + '\n\n'

        + '## 03 试试这一招\n' + r.micro_action.headline + '\n' + r.micro_action.steps.map(function(s) { return '- ' + s; }).join('\n') + '\n\n'

        + '## 04 读这一段\n' + r.further_reading + '\n\n'

        + '---\n让古老智慧，用今天的人听得懂的方式活着';



      navigator.clipboard.writeText(mdText).then(function() {

        showToast('已复制完整回应到剪贴板');

      }).catch(function() {

        showToast('复制完成');

      });

    };



    $('btnGenerateCard').onclick = function() {

      if (!appState.currentResult) return;

      var cd = prepareCardData(appState.currentResult);

      switchClientView('userCard');



      $('btnDownloadCardPng').onclick = function() {

        var pngUrl = drawRetinaCard(cd);

        var a = document.createElement('a');

        var dateStr = new Date().toISOString().slice(0, 10).replace(/-/g, '');

        a.href = pngUrl;

        a.download = 'wutang-card-' + dateStr + '-' + appState.currentResult.case_id + '.png';

        document.body.appendChild(a);

        a.click();

        a.remove();

        showToast('已保存高清东方解忧笺图片');

      };

    };



    $('btnReturnToResult').onclick = function() {

      switchClientView('userResult');

    };



    $('btnCopyCardText').onclick = function() {

      var text = $('cardTheme').textContent + '\n'

        + $('cardQuote').textContent + '\n'

        + $('cardSource').textContent + '\n\n'

        + '【现代解义】' + $('cardExp').textContent + '\n\n'

        + '【今晚微行动】' + $('cardAction').textContent + '\n\n'

        + '—— 悟堂 · 东方解忧笺';

      navigator.clipboard.writeText(text).then(function() {

        showToast('已复制解忧笺文');

      });

    };



    // 个人自存版 vs 公开分享版切换

    $('btnVerPersonal').onclick = function() {

      appState.cardPublicVersion = false;

      $('btnVerPersonal').classList.add('active');

      $('btnVerPublic').classList.remove('active');

      if (appState.currentResult) {

        prepareCardData(appState.currentResult);

      }

      showToast('已切换为「个人自存版」');

    };



    $('btnVerPublic').onclick = function() {

      appState.cardPublicVersion = true;

      $('btnVerPublic').classList.add('active');

      $('btnVerPersonal').classList.remove('active');

      if (appState.currentResult) {

        prepareCardData(appState.currentResult);

      }

      showToast('已切换为「公开分享版」（精选共读金句与通用微行动）');

    };



    // 反馈提交

    Array.prototype.forEach.call(document.querySelectorAll('.fb-btn'), function(b) {

      b.onclick = function() {

        Array.prototype.forEach.call(document.querySelectorAll('.fb-btn'), function(x) { x.classList.remove('selected'); });

        b.classList.add('selected');

        showToast('已选择：' + b.getAttribute('data-val'));

      };

    });



    $('btnSendFeedback').onclick = function() {

      var val = document.querySelector('.fb-btn.selected');

      var note = $('feedbackInput').value.trim();

      if (!val && !note) {

        showToast('请选择是否有帮助或填写一句话');

        return;

      }

      showToast('谢谢你告诉我们，我们会继续做得更温和');

      $('feedbackInput').value = '';

    };



    // 公开共读开关

    $('consentToggle').onchange = function(e) {

      appState.userConsent = e.target.checked;

      if (e.target.checked) {

        showToast('已开启：进入匿名内容脱敏审核流程（仍需主理人审核，不自动发布）');

      } else {

        showToast('已关闭公开共读授权');

      }

    };



    // ================= 主理人端事件绑定 =================

    Array.prototype.forEach.call(document.querySelectorAll('.studio-nav-btn'), function(btn) {

      btn.onclick = function() {

        switchStudioTab(btn.getAttribute('data-view'));

      };

    });



    $('btnQuickNewTask').onclick = function() { switchStudioTab('studioNewTask'); };

    $('btnGoReview').onclick = function() { switchStudioTab('studioReview'); };

    $('btnCancelTask').onclick = function() { switchStudioTab('studioOverview'); };

    $('btnBackToOverview').onclick = function() { switchStudioTab('studioOverview'); };

    $('btnPipelineToReview').onclick = function() { switchStudioTab('studioReview'); };



    // 新建任务中：预置案例选择联动

    var presetSelect = $('presetCaseSelect');

    presetSelect.innerHTML = SYNTHETIC_CASES.map(function(sc, idx) {

      return '<option value="' + idx + '">' + esc(sc.case_id) + ' ｜ ' + esc(sc.scenario_tag || '未定') + ' ｜ ' + snippet(sc.user_text, 20) + '</option>';

    }).join('');



    function updateNewTaskFormFromPreset(idx) {

      var sc = SYNTHETIC_CASES[idx];

      if (!sc) return;

      $('taskNameInput').value = '解忧任务 · ' + sc.case_id;

      $('taskContentText').value = sc.user_text;

      var hasConsent = (String(sc.consent_for_public_draft).toLowerCase() === 'true');

      $('taskConsentCheck').checked = hasConsent;

      checkConsentBlockRule();

    }



    presetSelect.onchange = function() {

      updateNewTaskFormFromPreset(presetSelect.value);

    };



    if (SYNTHETIC_CASES.length > 0) {

      updateNewTaskFormFromPreset(0);

    }



    $('taskSourceSelect').onchange = function() {

      if ($('taskSourceSelect').value === 'preset_demo') {

        $('presetCaseGroup').classList.remove('hidden');

      } else {

        $('presetCaseGroup').classList.add('hidden');

      }

    };



    // 授权阻断逻辑 (PRD 5.2 核心护栏)

    function checkConsentBlockRule() {

      var purposeRadio = document.querySelector('input[name="taskPurpose"]:checked');

      var isArticle = (purposeRadio && purposeRadio.value === 'article_draft');

      var isConsented = $('taskConsentCheck').checked;

      var alertBox = $('taskConsentAlert');

      var launchBtn = $('btnLaunchWorkflow');



      if (isArticle && !isConsented) {

        alertBox.classList.remove('hidden');

        launchBtn.setAttribute('disabled', 'true');

      } else {

        alertBox.classList.add('hidden');

        launchBtn.removeAttribute('disabled');

      }

    }



    Array.prototype.forEach.call(document.querySelectorAll('input[name="taskPurpose"]'), function(r) {

      r.onchange = checkConsentBlockRule;

    });

    $('taskConsentCheck').onchange = checkConsentBlockRule;



    $('btnLaunchWorkflow').onclick = function() {

      var taskId = 'WUTANG-TASK-' + Date.now().toString().slice(-4);

      openPipelineView(taskId);

      showToast('WorkBuddy 工作流已启动执行');

    };



    $('btnExportTaskReport').onclick = function() {

      showToast('已导出任务执行报告 markdown 文件');

    };



    // 草稿审核切换

    var draftSelect = $('draftCaseSelect');

    draftSelect.onchange = function() {

      renderStudioReview(draftSelect.value);

    };



    $('btnApproveDraft').onclick = function() {

      showToast('已标记为「主理人审核通过」（符合发布准备，不会自动发布）');

    };



    $('btnRejectDraft').onclick = function() {

      showToast('已记录退回修改意见，请重试相关 Skill');

    };



    $('btnExportDraftMd').onclick = function() {

      var draft = ARTICLE_DRAFTS[appState.currentDraftKey];

      if (!draft) return;

      var blob = new Blob([draft.content], { type: 'text/markdown;charset=utf-8' });

      var url = URL.createObjectURL(blob);

      var a = document.createElement('a');

      a.href = url;

      a.download = appState.currentDraftKey + '_article_draft.md';

      document.body.appendChild(a);

      a.click();

      a.remove();

      showToast('已导出 Markdown 草稿文件');

    };



    // 经典库与卡牌库搜索与筛选

    $('classicsSearchInput').oninput = renderClassicsList;

    $('classicsCategoryFilter').onchange = renderClassicsList;

    $('classicsStatusFilter').onchange = renderClassicsList;



    var cardTypeFilter = $('studioCardTypeFilter');

    if (cardTypeFilter) {

      cardTypeFilter.onchange = function() {

        renderStudioCards(cardTypeFilter.value);

      };

    }



    // 东方解忧笺（书笺）花样切换

    Array.prototype.forEach.call(document.querySelectorAll('.bm-pill'), function(pill) {

      pill.onclick = function() {

        applyBookmarkToDom(pill.getAttribute('data-bmid'));

        showToast('已切换书笺风格：' + pill.textContent.trim());

      };

    });



    // 禅意卡牌与书笺典藏弹窗交互

    var galleryModal = $('modalCardGallery');

    var btnOpenGallery = $('btnCardGalleryModal');

    var btnCloseGallery = $('closeGalleryModal');

    var btnCloseGalleryBottom = $('btnCloseGalleryBottom');



    if (btnOpenGallery && galleryModal) {

      btnOpenGallery.onclick = function() {

        galleryModal.classList.add('active');

        renderCardGallery('all');

      };

    }

    if (btnCloseGallery && galleryModal) {

      btnCloseGallery.onclick = function() {

        galleryModal.classList.remove('active');

      };

    }

    if (btnCloseGalleryBottom && galleryModal) {

      btnCloseGalleryBottom.onclick = function() {

        galleryModal.classList.remove('active');

      };

    }



    Array.prototype.forEach.call(document.querySelectorAll('#galleryFilterTabs .gallery-tab-btn'), function(tab) {

      tab.onclick = function() {

        Array.prototype.forEach.call(document.querySelectorAll('#galleryFilterTabs .gallery-tab-btn'), function(t) {

          t.classList.remove('active');

        });

        tab.classList.add('active');

        renderCardGallery(tab.getAttribute('data-filter'));

      };

    });

  }





  // ==========================================================================

  // PRD 3.0 全局模块业务控制器 (Growth / Wellbeing / Practice / Cards / Privacy)

  // ==========================================================================



  // --- 本地存储工具 ---

  function getStorageJson(key, defVal) {

    try {

      var r = localStorage.getItem(key);

      return r ? JSON.parse(r) : defVal;

    } catch(e) { return defVal; }

  }

  function setStorageJson(key, val) {

    try { localStorage.setItem(key, JSON.stringify(val)); } catch(e) {}

  }



  // --------------------------------------------------------------------------

  // 1. 成长记录模块 (Growth Section: F-10, F-11, F-12, F-13, F-14)

  // --------------------------------------------------------------------------

  var currentSelectedMoods = ['calm'];

  var currentSelectedEnergy = 'normal';

  var currentSelectedStress = 'low';



  function initGrowthModule() {

    // 情绪标签选择

    var chipGroup = $('moodChipGroup');

    if (chipGroup) {

      chipGroup.addEventListener('click', function(e) {

        var chip = e.target.closest('.mood-chip');

        if (!chip) return;

        var mood = chip.getAttribute('data-mood');

        chip.classList.toggle('active');

        if (chip.classList.contains('active')) {

          if (currentSelectedMoods.indexOf(mood) === -1) currentSelectedMoods.push(mood);

        } else {

          currentSelectedMoods = currentSelectedMoods.filter(function(m) { return m !== mood; });

        }

      });

    }



    // 精力水平单选

    var epGroup = $('energyPillGroup');

    if (epGroup) {

      epGroup.addEventListener('click', function(e) {

        var pill = e.target.closest('.level-pill');

        if (!pill) return;

        epGroup.querySelectorAll('.level-pill').forEach(function(p) { p.classList.remove('active'); });

        pill.classList.add('active');

        currentSelectedEnergy = pill.getAttribute('data-level');

      });

    }



    // 主观压力单选

    var spGroup = $('stressPillGroup');

    if (spGroup) {

      spGroup.addEventListener('click', function(e) {

        var pill = e.target.closest('.level-pill');

        if (!pill) return;

        spGroup.querySelectorAll('.level-pill').forEach(function(p) { p.classList.remove('active'); });

        pill.classList.add('active');

        currentSelectedStress = pill.getAttribute('data-level');

      });

    }



    // 提交签到

    var btnCheckin = $('btnSubmitCheckin');

    if (btnCheckin) {

      btnCheckin.onclick = function() {

        var note = $('checkinNoteInput') ? $('checkinNoteInput').value.trim() : '';

        var todayStr = new Date().toISOString().slice(0, 10);

        var record = {

          checkin_id: 'MC-' + todayStr + '-' + Math.random().toString(36).slice(2, 6),

          date: todayStr,

          moods: currentSelectedMoods.slice(),

          energy: currentSelectedEnergy,

          stress: currentSelectedStress,

          note: note,

          created_at: new Date().toISOString()

        };



        var list = getStorageJson('wutang_mood_checkins', []);

        list.unshift(record);

        setStorageJson('wutang_mood_checkins', list);



        showToast('已留下今日心境印记');

        var box = $('checkinFeedbackBox');

        if (box) box.classList.remove('hidden');

        renderMiniCalendar();

        updateDataSummary();

      };

    }



    // 重新签到与跳转

    if ($('btnCheckinReset')) {

      $('btnCheckinReset').onclick = function() {

        if ($('checkinFeedbackBox')) $('checkinFeedbackBox').classList.add('hidden');

      };

    }

    if ($('btnCheckinGoCard')) {

      $('btnCheckinGoCard').onclick = function() {

        switchMainTab('relief');

        handleClientAwarenessCard();

      };

    }



    // --- AI 日记整理 ---

    if ($('btnFillJournalSample')) {

      $('btnFillJournalSample').onclick = function() {

        if ($('journalInputText')) {

          $('journalInputText').value = '今天主管在例会上当众否定了我负责的模块，催促我重写。我当时非常难堪，整天脑子都停不下来，特别自责，甚至怀疑自己不适合这份工作。';

        }

      };

    }

    if ($('btnClearJournalInput')) {

      $('btnClearJournalInput').onclick = function() {

        if ($('journalInputText')) $('journalInputText').value = '';

        if ($('journalStructuredResult')) $('journalStructuredResult').classList.add('hidden');

      };

    }

    if ($('btnAiOrganizeJournal')) {

      $('btnAiOrganizeJournal').onclick = function() {

        var raw = $('journalInputText') ? $('journalInputText').value.trim() : '';

        if (!raw) {

          showToast('请先输入今天的日常倾诉');

          return;

        }



        var btn = $('btnAiOrganizeJournal');

        btn.disabled = true;

        btn.textContent = '🌿 悟堂 AI 正在倾听与梳理…';



        fetch('http://localhost:8000/api/journal/organize', {

          method: 'POST',

          headers: { 'Content-Type': 'application/json' },

          body: JSON.stringify({ raw_text: raw, consent_to_save: true })

        }).then(function(r) { return r.json(); })

          .then(function(data) {

            btn.disabled = false;

            btn.textContent = '🌿 AI 结构化梳理心绪';

            var res = (data && data.structured_journal) ? data.structured_journal : null;

            if (res) renderJournalResult(res, raw);

          })

          .catch(function(err) {

            btn.disabled = false;

            btn.textContent = '🌿 AI 结构化梳理心绪';

            // 离线高质量兜底提炼

            var fallback = {

              event_summary: raw.slice(0, 70) + (raw.length > 70 ? '…' : ''),

              thoughts: '反复在心头重播被批评的场景，陷入「我不行」的自我怀疑。',

              feelings: ['难堪', '自责', '疲惫', '内耗'],

              possible_needs: '【待你确认】希望付出被客观尊重，工作有明确改进指引而非笼统指责。',

              next_step: '今晚先把情绪和事实写在纸上，明天以微信文字向主管确认两点具体改进细节。'

            };

            renderJournalResult(fallback, raw);

          });

      };

    }



    if ($('btnSaveJournalToLocal')) {

      $('btnSaveJournalToLocal').onclick = function() {

        var list = getStorageJson('wutang_journals', []);

        var todayStr = new Date().toISOString().slice(0, 10);

        list.unshift({

          id: 'J-' + todayStr + '-' + Math.random().toString(36).slice(2, 6),

          date: todayStr,

          event: $('jResEvent') ? $('jResEvent').textContent : '',

          thoughts: $('jResThoughts') ? $('jResThoughts').textContent : '',

          needs: $('jResNeeds') ? $('jResNeeds').textContent : '',

          next_step: $('jResNextStep') ? $('jResNextStep').textContent : '',

          created_at: new Date().toISOString()

        });

        setStorageJson('wutang_journals', list);

        showToast('日记已妥善安放在本地成长记录中');

        if ($('journalStructuredResult')) $('journalStructuredResult').classList.add('hidden');

        if ($('journalInputText')) $('journalInputText').value = '';

        updateDataSummary();

      };

    }



    if ($('btnDiscardJournal')) {

      $('btnDiscardJournal').onclick = function() {

        if ($('journalStructuredResult')) $('journalStructuredResult').classList.add('hidden');

      };

    }



    // --- 微行动反馈 ---

    var afGroup = $('actionFeedbackBtnGroup');

    if (afGroup) {

      afGroup.addEventListener('click', function(e) {

        var btn = e.target.closest('button');

        if (!btn) return;

        var status = btn.getAttribute('data-action-status');

        var reviews = getStorageJson('wutang_action_reviews', []);

        reviews.unshift({

          status: status,

          date: new Date().toISOString().slice(0, 10),

          action: $('currentMicroActionTitle') ? $('currentMicroActionTitle').textContent : ''

        });

        setStorageJson('wutang_action_reviews', reviews);



        var tip = $('actionFeedbackToast');

        if (tip) {

          tip.classList.remove('hidden');

          if (status === 'completed') tip.textContent = '已记录：好样的！哪怕只是一小步，也是对自己的温柔善待。';

          else if (status === 'partial') tip.textContent = '已记录：能做一部分已经非常棒了，跟随身心节奏，不急于求成。';

          else if (status === 'not_started') tip.textContent = '已记录：完全没关系，今晚先把心安顿好，明天随时可以重新开始。';

          else if (status === 'unsuitable') tip.textContent = '已记录：听从你的感觉，方法很多，我们随时换一个更舒适的小动作。';

        }

        showToast('已记录行动复盘反馈');

        updateDataSummary();

      });

    }

  }



  function renderJournalResult(res, raw) {

    if ($('jResEvent')) $('jResEvent').textContent = res.event_summary || raw;

    if ($('jResThoughts')) $('jResThoughts').textContent = res.thoughts || '';

    if ($('jResNeeds')) $('jResNeeds').textContent = res.possible_needs || '';

    if ($('jResNextStep')) $('jResNextStep').textContent = res.next_step || '';



    var fContainer = $('jResFeelings');

    if (fContainer) {

      var arr = Array.isArray(res.feelings) ? res.feelings : ['紧绷', '疲惫'];

      fContainer.innerHTML = arr.map(function(w) {

        return '<span class="badge rev" style="font-size:12px;">' + esc(w) + '</span>';

      }).join('');

    }



    if ($('journalStructuredResult')) $('journalStructuredResult').classList.remove('hidden');

    showToast('AI 结构化整理已生成，请检查并纠偏');

  }



  function renderGrowthSection() {

    renderMiniCalendar();

    // 渲染今日日期

    var badge = $('checkinTodayDateBadge');

    if (badge) badge.textContent = '今日：' + new Date().toISOString().slice(0, 10);

  }



  function renderMiniCalendar() {

    var grid = $('miniCalendarGrid');

    if (!grid) return;

    var checkins = getStorageJson('wutang_mood_checkins', []);

    var dateSet = {};

    checkins.forEach(function(c) { if (c.date) dateSet[c.date] = true; });



    var now = new Date();

    var year = now.getFullYear();

    var month = now.getMonth();

    var daysInMonth = new Date(year, month + 1, 0).getDate();

    var todayStr = now.toISOString().slice(0, 10);



    var html = '';

    var weekHeaders = ['日', '一', '二', '三', '四', '五', '六'];

    weekHeaders.forEach(function(h) {

      html += '<div style="font-weight:600;font-size:11px;color:var(--color-muted);padding:4px 0;">' + h + '</div>';

    });



    var firstDayOfWeek = new Date(year, month, 1).getDay();

    for (var i = 0; i < firstDayOfWeek; i++) {

      html += '<div class="mini-cal-day" style="opacity:0.25;">·</div>';

    }



    for (var d = 1; d <= daysInMonth; d++) {

      var dStr = year + '-' + String(month + 1).padStart(2, '0') + '-' + String(d).padStart(2, '0');

      var isToday = (dStr === todayStr);

      var hasCheckin = Boolean(dateSet[dStr]);

      var cls = 'mini-cal-day' + (isToday ? ' today' : '') + (hasCheckin ? ' has-checkin' : '');

      html += '<div class="' + cls + '" title="' + dStr + (hasCheckin ? ' 已签到' : '') + '">' + d + (hasCheckin ? ' 🌿' : '') + '</div>';

    }

    grid.innerHTML = html;



    // 每周回顾文案

    var summaryEl = $('weeklyReviewSummary');

    if (summaryEl) {

      if (checkins.length === 0) {

        summaryEl.textContent = '暂无签到记录。在上方留下你的第一次心境印记，悟堂将为你记录每日身心起伏。';

      } else if (checkins.length < 3) {

        summaryEl.textContent = '目前累计已留下 ' + checkins.length + ' 次觉察记录。根据 PRD 3.0 规范：记录较少时暂不下定论，请依你的节奏自然记录。';

      } else {

        summaryEl.textContent = '过去阶段已累计记录 ' + checkins.length + ' 次心境。你常在疲惫时能主动停下来为自己留白，这就是最踏实的自我关照。';

      }

    }

  }





  // --------------------------------------------------------------------------

  // 2. 心境健康中心模块 (Wellbeing: F-16, F-17, 18.9, 18.11)

  // --------------------------------------------------------------------------

  var pss10UserAnswers = new Array(10).fill(null);



  function initWellbeingModule() {

    // 展开 PSS-10

    if ($('btnOpenPss10')) {

      $('btnOpenPss10').onclick = function() {

        renderPss10Questions();

        if ($('pss10QuizContainer')) $('pss10QuizContainer').classList.remove('hidden');

        if ($('pss10ResultCard')) $('pss10ResultCard').classList.add('hidden');

        $('pss10QuizContainer').scrollIntoView({ behavior: 'smooth' });

      };

    }

    if ($('btnClosePss10')) {

      $('btnClosePss10').onclick = function() {

        if ($('pss10QuizContainer')) $('pss10QuizContainer').classList.add('hidden');

      };

    }



    // 提交 PSS-10

    if ($('btnSubmitPss10')) {

      $('btnSubmitPss10').onclick = function() {

        for (var i = 0; i < 10; i++) {

          if (pss10UserAnswers[i] === null) {

            showToast('请先完成第 ' + (i + 1) + ' 题作答');

            return;

          }

        }



        // 调用确定性计分接口

        fetch('http://localhost:8000/api/wellbeing/score', {

          method: 'POST',

          headers: { 'Content-Type': 'application/json' },

          body: JSON.stringify({

            instrument_id: 'pss-10',

            answers: pss10UserAnswers,

            consent_to_record: true

          })

        }).then(function(r) { return r.json(); })

          .then(function(res) {

            if (res.success) renderPss10Report(res);

            else showToast(res.message || '计分失败');

          })

          .catch(function() {

            // 离线确定性计分兜底 (严格按照 PSS-10 规则：4,5,7,8 反向计分)

            var reverseIdx = [3, 4, 6, 7];

            var total = 0;

            for (var j = 0; j < 10; j++) {

              var v = pss10UserAnswers[j];

              total += (reverseIdx.indexOf(j) !== -1 ? (4 - v) : v);

            }

            var lvl = total <= 13 ? 'low' : (total <= 26 ? 'moderate' : 'high');

            var lvlLabel = total <= 13 ? '轻度压力' : (total <= 26 ? '中度压力' : '较高压力');

            var flag = (pss10UserAnswers[9] >= 3 && total >= 28);

            renderPss10Report({

              success: true,

              total_score: total,

              level: lvl,

              level_label: lvlLabel,

              summary: total <= 13 ? '你近期的知觉压力处于较低或平稳范围，能够较好地应对日常生活与工作节奏。' : (total <= 26 ? '你近期体验到了生活中的不可控感或挑战，情绪与精力有所消耗，建议有意识安排身心休息与微行动调适。' : '你近期承受的主观负荷较重，可能感到多项琐事超出个人掌控。这不是你的软弱，建议暂缓次要事务，必要时与专业心理人士聊聊。'),

              mindset_insight: '知觉压力反映过去一个月的身心负荷感，不是性格定论。允许自己拥有起伏。',

              oriental_wisdom_angle: '《大学》云：『知止而后有定，定而后能静。』在繁杂之中，先为自己找到一个明确的暂停锚点。',

              next_steps: ['睡前做 3 次平稳深呼吸', '将事实与担忧分栏写下', '如持续超过两周建议联系专业咨询师'],

              is_safety_flagged: flag,

              safety_message: flag ? '检测到你近期感到困难积聚且负荷沉重。建议参考下方全国心理援助热线或专业资源导航，给自己一份专业支持。' : ''

            });

          });

      };

    }



    if ($('btnRetakePss10')) {

      $('btnRetakePss10').onclick = function() {

        pss10UserAnswers.fill(null);

        renderPss10Questions();

        if ($('pss10ResultCard')) $('pss10ResultCard').classList.add('hidden');

        if ($('pss10QuizContainer')) $('pss10QuizContainer').classList.remove('hidden');

      };

    }



    if ($('btnSavePss10History')) {

      $('btnSavePss10History').onclick = function() {

        var scoreVal = $('pss10ScoreVal') ? $('pss10ScoreVal').textContent : '';

        var lvl = $('pss10LevelBadge') ? $('pss10LevelBadge').textContent : '';

        var list = getStorageJson('wutang_assessments', []);

        list.unshift({

          instrument: 'PSS-10',

          score: scoreVal,

          level: lvl,

          date: new Date().toISOString().slice(0, 10),

          created_at: new Date().toISOString()

        });

        setStorageJson('wutang_assessments', list);

        showToast('自评报告已安全存储至本地');

        updateDataSummary();

      };

    }



    // 资源导航地区过滤

    var regSelect = $('resourceRegionFilter');

    if (regSelect) {

      regSelect.onchange = function() {

        renderResourcesList(this.value);

      };

    }



    // 生成转介沟通清单

    if ($('btnGenerateReferral')) {

      $('btnGenerateReferral').onclick = function() {

        var complaint = $('referralComplaintInput') ? $('referralComplaintInput').value.trim() : '';

        var duration = $('referralDurationInput') ? $('referralDurationInput').value.trim() : '约2-4周';

        if (!complaint) {

          showToast('请先简述你的主要困扰');

          return;

        }



        var btn = $('btnGenerateReferral');

        btn.disabled = true;

        btn.textContent = '正在为你整理沟通清单…';



        fetch('http://localhost:8000/api/referral/summary', {

          method: 'POST',

          headers: { 'Content-Type': 'application/json' },

          body: JSON.stringify({

            main_complaint: complaint,

            duration: duration,

            assessment_score: $('pss10ScoreVal') ? parseInt($('pss10ScoreVal').textContent) : null

          })

        }).then(function(r) { return r.json(); })

          .then(function(data) {

            btn.disabled = false;

            btn.textContent = '一键生成就医/面询沟通清单';

            if (data && data.summary) renderReferralSummary(data.summary);

          })

          .catch(function() {

            btn.disabled = false;

            btn.textContent = '一键生成就医/面询沟通清单';

            renderReferralSummary({

              summary_title: '日常压力与身心负荷沟通参考清单',

              key_symptoms: [complaint, '持续时间：' + duration, '近期感到注意力分散与身心疲惫'],

              impact_on_daily_life: '日常睡眠节律偶有波动，对多项并行的事务感到压力过载。',

              questions_for_specialist: [

                '针对我目前的压力状态，有哪些适合日常练习的身体放松或认知调整方法？',

                '是否建议进行更系统的心理咨询或进一步临床评估？'

              ]

            });

          });

      };

    }



    if ($('btnCopyReferralSummary')) {

      $('btnCopyReferralSummary').onclick = function() {

        var text = $('refSumBody') ? $('refSumBody').innerText : '';

        if (navigator.clipboard) {

          navigator.clipboard.writeText(text).then(function() { showToast('面询清单已复制到剪贴板'); });

        } else {

          showToast('复制成功');

        }

      };

    }

  }



  function renderPss10Questions() {

    var listEl = $('pss10QuestionsList');

    if (!listEl) return;

    var inst = (INSTRUMENTS || []).find(function(it) { return it.instrument_id === 'pss-10'; });

    var items = (inst && inst.items) ? inst.items : [

      { id: 1, text: "在过去的一个月中，你是否因为某些意料之外的事情发生而感到心烦意乱？" },

      { id: 2, text: "在过去的一个月中，你是否感到自己无法控制生活中的重要事情？" },

      { id: 3, text: "在过去的一个月中，你是否感到神经过敏或感到压力很大？" },

      { id: 4, text: "在过去的一个月中，你是否感到自己能充满信心地处理个人问题？" },

      { id: 5, text: "在过去的一个月中，你是否感到事情正在按照你的意愿顺利发展？" },

      { id: 6, text: "在过去的一个月中，你是否发现自己无法处理所有必须要做的事情？" },

      { id: 7, text: "在过去的一个月中，你是否能够有效地控制生活中的烦恼与波动？" },

      { id: 8, text: "在过去的一个月中，你是否感到自己一切都在掌握之中？" },

      { id: 9, text: "在过去的一个月中，你是否因为某些无法掌控的事情而感到生气或愤怒？" },

      { id: 10, text: "在过去的一个月中，你是否感到生活中的困难积聚太多，自己已经难以克服？" }

    ];



    var options = [

      { v: 0, l: "从不 (0)" },

      { v: 1, l: "很少 (1)" },

      { v: 2, l: "有时 (2)" },

      { v: 3, l: "经常 (3)" },

      { v: 4, l: "总是 (4)" }

    ];



    var html = items.map(function(item, idx) {

      var currentVal = pss10UserAnswers[idx];

      var optHtml = options.map(function(opt) {

        var isSel = (currentVal === opt.v);

        return '<button type="button" class="scale-radio-btn' + (isSel ? ' selected' : '') + '" data-qidx="' + idx + '" data-val="' + opt.v + '">' + opt.l + '</button>';

      }).join('');



      return '<div class="assessment-question-item">'

        + '  <div class="assessment-question-title">' + (idx + 1) + '. ' + esc(item.text) + '</div>'

        + '  <div class="scale-options-row">' + optHtml + '</div>'

        + '</div>';

    }).join('');



    listEl.innerHTML = html;



    listEl.onclick = function(e) {

      var btn = e.target.closest('.scale-radio-btn');

      if (!btn) return;

      var qIdx = parseInt(btn.getAttribute('data-qidx'));

      var val = parseInt(btn.getAttribute('data-val'));

      pss10UserAnswers[qIdx] = val;

      renderPss10Questions();

    };

  }



  function renderPss10Report(data) {

    if ($('pss10QuizContainer')) $('pss10QuizContainer').classList.add('hidden');

    if ($('pss10ResultCard')) $('pss10ResultCard').classList.remove('hidden');



    if ($('pss10ScoreVal')) $('pss10ScoreVal').textContent = data.total_score;

    if ($('pss10LevelBadge')) $('pss10LevelBadge').textContent = data.level_label || '测评完成';

    if ($('pss10SummaryText')) $('pss10SummaryText').textContent = data.summary || '';

    if ($('pss10WisdomText')) $('pss10WisdomText').textContent = data.oriental_wisdom_angle || data.mindset_insight || '';



    var stepUl = $('pss10NextStepsList');

    if (stepUl) {

      var steps = Array.isArray(data.next_steps) ? data.next_steps : ['保持规律作息', '尝试轻度微行动'];

      stepUl.innerHTML = steps.map(function(s) { return '<li>' + esc(s) + '</li>'; }).join('');

    }



    var alertBox = $('pss10SafetyAlert');

    if (alertBox) {

      if (data.is_safety_flagged) {

        alertBox.classList.remove('hidden');

        if ($('pss10SafetyText')) $('pss10SafetyText').textContent = data.safety_message;

      } else {

        alertBox.classList.add('hidden');

      }

    }



    $('pss10ResultCard').scrollIntoView({ behavior: 'smooth' });

  }



  function renderResourcesList(filterRegion) {

    var grid = $('resourceListGrid');

    if (!grid) return;

    var list = MENTAL_RESOURCES || [];

    filterRegion = filterRegion || '全部';



    var filtered = list.filter(function(r) {

      if (filterRegion === '全部') return true;

      if (filterRegion === '全国') return r.region === '全国';

      return r.region === filterRegion || r.region === '全国';

    });



    if (filtered.length === 0) {

      grid.innerHTML = '<div style="grid-column:1/-1;padding:24px;text-align:center;color:var(--color-muted);">当前地区暂未检索到已核验的常设专线</div>';

      return;

    }



    grid.innerHTML = filtered.map(function(item) {

      var isHotline = (item.service_type === 'hotline');

      var typeBadge = isHotline ? '<span class="badge ok">免费热线</span>' : '<span class="badge rev">公立专科</span>';

      return '<div class="resource-card">'

        + '  <div>'

        + '    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">'

        + '      ' + typeBadge

        + '      <span style="font-size:11px;color:var(--color-muted);">' + esc(item.region) + '</span>'

        + '    </div>'

        + '    <h4 style="margin:0 0 6px;font-size:15px;color:var(--color-ink);font-weight:600;">' + esc(item.resource_name) + '</h4>'

        + '    <div style="font-size:12.5px;color:var(--color-primary);font-weight:bold;margin-bottom:6px;">'

        + '      📞 <a href="tel:' + esc(item.contact_info) + '" style="color:var(--color-primary);text-decoration:none;">' + esc(item.contact_info) + '</a>'

        + '    </div>'

        + '    <div style="font-size:12px;color:var(--color-muted);line-height:1.5;">' + esc(item.availability_note || '') + '</div>'

        + '  </div>'

        + '  <div style="margin-top:10px;padding-top:8px;border-top:1px dashed var(--color-border);font-size:11px;color:var(--color-muted);display:flex;justify-content:space-between;">'

        + '    <span>出处：' + esc(item.source_url ? item.source_url.slice(0, 12) + '…' : '官方') + '</span>'

        + '    <span>核验：' + esc(item.last_verified_at) + '</span>'

        + '  </div>'

        + '</div>';

    }).join('');

  }



  function renderReferralSummary(sum) {

    var box = $('referralSummaryBox');

    if (!box) return;

    box.classList.remove('hidden');



    if ($('refSumTitle')) $('refSumTitle').textContent = sum.summary_title || '日常压力沟通参考清单';



    var html = '';

    html += '<div style="margin-bottom:8px;"><strong>一、核心主诉梳理：</strong></div>';

    html += '<ul style="margin:0 0 10px;padding-left:20px;">' + (sum.key_symptoms || []).map(function(s) { return '<li>' + esc(s) + '</li>'; }).join('') + '</ul>';



    if (sum.impact_on_daily_life) {

      html += '<div style="margin-bottom:4px;"><strong>二、日常身心影响：</strong></div>';

      html += '<p style="margin:0 0 10px;">' + esc(sum.impact_on_daily_life) + '</p>';

    }



    if (sum.questions_for_specialist && sum.questions_for_specialist.length) {

      html += '<div style="margin-bottom:4px;"><strong>三、期望向医生/咨询师咨询的问题：</strong></div>';

      html += '<ol style="margin:0;padding-left:20px;">' + sum.questions_for_specialist.map(function(q) { return '<li>' + esc(q) + '</li>'; }).join('') + '</ol>';

    }



    if ($('refSumBody')) $('refSumBody').innerHTML = html;

    box.scrollIntoView({ behavior: 'smooth' });

  }



  function renderWellbeingSection() {

    renderResourcesList('全部');

  }





  // --------------------------------------------------------------------------

  // 3. 情境练习室模块 (Practice Room: F-15 / 18.8)

  // --------------------------------------------------------------------------

  var currentPracticeScenario = null;

  var practiceChatHistory = [];



  function initPracticeModule() {

    renderPracticeScenarioCards();



    if ($('btnResetPracticeScenario')) {

      $('btnResetPracticeScenario').onclick = function() {

        if (currentPracticeScenario) startPracticeScenario(currentPracticeScenario);

      };

    }



    if ($('btnSendPracticeMessage')) {

      $('btnSendPracticeMessage').onclick = sendPracticeMessage;

    }

    if ($('practiceDraftInput')) {

      $('practiceDraftInput').onkeydown = function(e) {

        if (e.key === 'Enter') sendPracticeMessage();

      };

    }

  }



  function renderPracticeScenarioCards() {

    var grid = $('practiceScenarioCardsGrid');

    if (!grid) return;

    var list = PRACTICE_SCENARIOS || [];



    grid.innerHTML = list.map(function(sc, idx) {

      return '<div class="theme-pack-card" data-scid="' + sc.scenario_id + '">'

        + '  <span class="badge ok" style="font-size:11px;margin-bottom:6px;">' + esc(sc.category) + '</span>'

        + '  <h4 style="margin:0 0 6px;font-size:16px;color:var(--color-ink);">' + esc(sc.title) + '</h4>'

        + '  <p style="margin:0 0 12px;font-size:12.5px;color:var(--color-muted);line-height:1.5;">' + esc(sc.description) + '</p>'

        + '  <button class="btn sm secondary" style="width:100%;">进入练习 →</button>'

        + '</div>';

    }).join('');



    grid.onclick = function(e) {

      var card = e.target.closest('.theme-pack-card');

      if (!card) return;

      var scId = card.getAttribute('data-scid');

      var target = (PRACTICE_SCENARIOS || []).find(function(s) { return s.scenario_id === scId; });

      if (target) startPracticeScenario(target);

    };



    if (list.length > 0 && !currentPracticeScenario) {

      startPracticeScenario(list[0]);

    }

  }



  function startPracticeScenario(sc) {

    currentPracticeScenario = sc;

    practiceChatHistory = [];



    if ($('practiceRoomTitle')) $('practiceRoomTitle').textContent = sc.title;

    if ($('practiceRoomRoleDesc')) $('practiceRoomRoleDesc').textContent = 'AI 扮演对象：' + sc.ai_role;



    // AI 开场白

    practiceChatHistory.push({

      role: 'ai',

      content: sc.opening_line || '「你好，我们可以开始了。」'

    });



    renderPracticeChat();

    if ($('practiceFeedbackBox')) $('practiceFeedbackBox').classList.add('hidden');

    if ($('practiceDraftInput')) {

      $('practiceDraftInput').value = '';

      $('practiceDraftInput').focus();

    }

  }



  function renderPracticeChat() {

    var win = $('practiceChatWindow');

    if (!win) return;

    win.innerHTML = practiceChatHistory.map(function(msg) {

      var isAi = (msg.role === 'ai');

      return '<div class="chat-msg ' + (isAi ? 'role-ai' : 'role-user') + '">' + esc(msg.content) + '</div>';

    }).join('');

    win.scrollTop = win.scrollHeight;

  }



  function sendPracticeMessage() {

    var input = $('practiceDraftInput');

    if (!input) return;

    var text = input.value.trim();

    if (!text) {

      showToast('请输入你练习的一句话');

      return;

    }



    practiceChatHistory.push({ role: 'user', content: text });

    renderPracticeChat();

    input.value = '';



    var btn = $('btnSendPracticeMessage');

    if (btn) { btn.disabled = true; btn.textContent = '思考中…'; }



    fetch('http://localhost:8000/api/practice/chat', {

      method: 'POST',

      headers: { 'Content-Type': 'application/json' },

      body: JSON.stringify({

        scenario_id: currentPracticeScenario ? currentPracticeScenario.scenario_id : 'general',

        scenario_title: currentPracticeScenario ? currentPracticeScenario.title : '沟通练习',

        ai_role: currentPracticeScenario ? currentPracticeScenario.ai_role : '对话对象',

        user_draft: text,

        history: practiceChatHistory.slice(0, -1).map(function(m) {

          return {

            role: (m.role === 'ai' || m.role === 'assistant') ? 'assistant' : 'user',

            content: m.content

          };

        })

      })

    }).then(function(r) { return r.json(); })

      .then(function(data) {

        if (btn) { btn.disabled = false; btn.textContent = '发送练习'; }

        var res = (data && data.practice_result) ? data.practice_result : null;

        if (res) handlePracticeReply(res);

      })

      .catch(function() {

        if (btn) { btn.disabled = false; btn.textContent = '发送练习'; }

        // 离线高质量兜底

        handlePracticeReply({

          role_reply: '「我听明白了。不过这事确实比较突然，你看看还有什么其他折中的办法吗？」',

          feedback: {

            boundary: '基本表达了边界，态度坚决。',

            tone: '语气平实，无过分对抗感。',

            advice: '若能先表达对事情重要性的理解，再说明自身饱和度，合作体面更完整。'

          },

          alternatives: [

            '「我理解这个报表很急。不过我手头刚好有两个必须今晚闭环的数据要交，实在挪不出完整时间，你看我明天一早帮你看看行吗？」',

            '「今晚我的工单实在排满了。你可以先把上周的模板套进去，核心部分我们明天再对齐。」'

          ]

        });

      });

  }



  function handlePracticeReply(res) {

    if (res.role_reply) {

      practiceChatHistory.push({ role: 'ai', content: res.role_reply });

      renderPracticeChat();

    }



    var fbBox = $('practiceFeedbackBox');

    if (fbBox) {

      fbBox.classList.remove('hidden');

      var fb = res.feedback || {};

      if ($('pfBoundaryText')) $('pfBoundaryText').textContent = fb.boundary || '边界基本清晰。';

      if ($('pfToneText')) $('pfToneText').textContent = fb.tone || '语气得体。';

      if ($('pfAdviceText')) $('pfAdviceText').textContent = fb.advice || '建议保持平视沟通。';



      var altBox = $('pfAlternativesContainer');

      if (altBox) {

        var alts = res.alternatives || [];

        altBox.innerHTML = alts.map(function(alt) {

          return '<div class="alt-quote-card">'

            + '  <span>' + esc(alt) + '</span>'

            + '  <button class="btn sm secondary" onclick="copyPracticeAlt(this)" data-alt="' + esc(alt) + '">复制范式</button>'

            + '</div>';

        }).join('');

      }

      fbBox.scrollIntoView({ behavior: 'smooth' });

    }

  }



  window.copyPracticeAlt = function(btn) {

    var text = btn.getAttribute('data-alt');

    if (navigator.clipboard) {

      navigator.clipboard.writeText(text).then(function() { showToast('范式已复制'); });

    } else {

      showToast('范式已复制');

    }

  };



  function renderPracticeSection() {

    renderPracticeScenarioCards();

  }





  // --------------------------------------------------------------------------

  // 4. 卡牌典藏与主题卡牌包模块 (Theme Packs: F-18 / 18.12)

  // --------------------------------------------------------------------------

  var currentSelectedPack = null;



  function initCardsModule() {

    renderThemePackGrid();

    renderFavoriteCards();

  }



  function renderThemePackGrid() {

    var grid = $('themePackGridContainer');

    if (!grid) return;

    var packs = THEME_PACKS || [];



    grid.innerHTML = packs.map(function(p) {

      var isAct = (currentSelectedPack && currentSelectedPack.pack_id === p.pack_id);

      return '<div class="theme-pack-card' + (isAct ? ' active' : '') + '" data-packid="' + p.pack_id + '">'

        + '  <div style="font-size:26px;margin-bottom:8px;">' + p.icon + '</div>'

        + '  <h3 style="font-family:var(--font-serif);margin:0 0 4px;font-size:18px;">' + esc(p.name) + '</h3>'

        + '  <div style="font-size:12.5px;color:var(--color-primary);font-weight:500;margin-bottom:8px;">' + esc(p.tagline) + '</div>'

        + '  <p style="margin:0;font-size:12px;color:var(--color-muted);line-height:1.6;">' + esc(p.description) + '</p>'

        + '  <div style="margin-top:12px;display:flex;justify-content:space-between;align-items:center;">'

        + '    <span style="font-size:11px;color:var(--color-gold);">3 张核心牌组</span>'

        + '    <span style="font-size:12px;color:var(--color-primary);font-weight:600;">展开卡组 →</span>'

        + '  </div>'

        + '</div>';

    }).join('');



    grid.onclick = function(e) {

      var card = e.target.closest('.theme-pack-card');

      if (!card) return;

      var pid = card.getAttribute('data-packid');

      var pack = (THEME_PACKS || []).find(function(p) { return p.pack_id === pid; });

      if (pack) selectThemePack(pack);

    };



    if (packs.length > 0 && !currentSelectedPack) {

      selectThemePack(packs[0]);

    }

  }



  function selectThemePack(pack) {

    currentSelectedPack = pack;

    renderThemePackGrid();



    if ($('themePackDetailTitle')) $('themePackDetailTitle').textContent = pack.name + ' · 核心卡牌包 (' + pack.icon + ')';

    if ($('themePackDetailDesc')) $('themePackDetailDesc').textContent = pack.tagline + ' —— ' + pack.description;



    var container = $('themePackCardsList');

    if (!container) return;



    var allCards = [].concat(CARDS_MINDSET, CARDS_WISDOM, CARDS_ACTION);

    var matched = allCards.filter(function(c) {

      return pack.card_ids && pack.card_ids.indexOf(c.card_id) !== -1;

    });



    if (matched.length === 0) {

      matched = allCards.slice(0, 3);

    }



    container.innerHTML = matched.map(function(card) {

      return renderSingleCardHtml(card);

    }).join('');

  }



  function renderSingleCardHtml(card) {

    var typeName = card.card_type === 'mindset' ? '心境牌 · 看见自己' : (card.card_type === 'wisdom' ? '东方智慧牌 · 换个视角' : '行动牌 · 走出一步');

    var badgeClass = card.card_type === 'mindset' ? 'ok' : (card.card_type === 'wisdom' ? 'gold' : 'rev');

    var favList = getStorageJson('wutang_favorite_cards', []);

    var isFav = (favList.indexOf(card.card_id) !== -1);



    var content = card.front_text || card.quote || card.action_text || card.short_description || '';

    var source = card.source_title ? ('《' + card.source_title + '·' + (card.source_section || '') + '》') : '';



    return '<div class="studio-card-item">'

      + '  <div class="studio-card-header">'

      + '    <span class="badge ' + badgeClass + '">' + typeName + '</span>'

      + '    <span style="font-size:12px;color:var(--color-muted);">' + esc(card.card_id) + '</span>'

      + '  </div>'

      + '  <h3 class="studio-card-title">' + esc(card.title) + '</h3>'

      + '  <p class="studio-card-quote serif">“' + esc(content) + '”</p>'

      + (source ? ('<div class="studio-card-meta">出处：' + esc(source) + '</div>') : '')

      + '  <div class="studio-card-actions">'

      + '    <button class="btn sm ' + (isFav ? 'secondary' : 'ghost') + '" onclick="toggleFavoriteCard(\'' + card.card_id + '\')">'

      + (isFav ? '★ 已珍藏' : '☆ 珍藏此卡')

      + '    </button>'

      + '  </div>'

      + '</div>';

  }



  window.toggleFavoriteCard = function(cardId) {

    var list = getStorageJson('wutang_favorite_cards', []);

    var idx = list.indexOf(cardId);

    if (idx !== -1) {

      list.splice(idx, 1);

      showToast('已取消珍藏');

    } else {

      list.push(cardId);

      showToast('已珍藏至我的卡牌库');

    }

    setStorageJson('wutang_favorite_cards', list);

    renderFavoriteCards();

    if (currentSelectedPack) selectThemePack(currentSelectedPack);

    updateDataSummary();

  };



  function renderFavoriteCards() {

    var container = $('favCardsContainer');

    if (!container) return;

    var favIds = getStorageJson('wutang_favorite_cards', []);

    var countNotice = $('favCardsCountNotice');

    if (countNotice) countNotice.textContent = '当前珍藏 ' + favIds.length + ' 张启发卡牌';



    if (favIds.length === 0) {

      container.innerHTML = '<div style="grid-column:1/-1;padding:24px;text-align:center;color:var(--color-muted);">暂无珍藏卡牌。在浏览或解忧时点击「珍藏此卡」即可沉淀在此。</div>';

      return;

    }



    var allCards = [].concat(CARDS_MINDSET, CARDS_WISDOM, CARDS_ACTION);

    var cards = allCards.filter(function(c) { return favIds.indexOf(c.card_id) !== -1; });

    container.innerHTML = cards.map(function(c) { return renderSingleCardHtml(c); }).join('');

  }



  
  // ==========================================================================
  // 108 百八常道卡牌人生图鉴与 A4 拼版打印引擎
  // ==========================================================================
  var currentPantheonFilter = 'all';

  function renderPantheonSection() {
    var grid = $('pantheonCardsGrid');
    if (!grid) return;
    var cards = (window.__WUTANG_DATA__ && window.__WUTANG_DATA__.zenCards108) ? window.__WUTANG_DATA__.zenCards108 : [];
    if (!cards.length) {
      grid.innerHTML = '<div style="grid-column:1/-1;text-align:center;padding:20px;color:var(--color-muted);">卡牌图鉴资产正在加载中...</div>';
      return;
    }

    var list = (currentPantheonFilter === 'all')
      ? cards
      : cards.filter(function(c) { return c.school === currentPantheonFilter; });

    grid.innerHTML = list.map(function(c) {
      var schColor = (c.school === 'daoism') ? '#2B4C5F' : ((c.school === 'buddhism') ? '#B58900' : '#8E2927');
      var schName = (c.school === 'daoism') ? '道学·老子' : ((c.school === 'buddhism') ? '释学·佛陀' : '儒学·孔子');

      return '<div style="background:#FFF;border:1px solid var(--color-border);border-radius:10px;padding:12px;display:flex;flex-direction:column;justify-content:space-between;box-shadow:0 2px 6px rgba(0,0,0,0.02);transition:all 0.2s;" onmouseover="this.style.transform=\'translateY(-2px)\'" onmouseout="this.style.transform=\'none\'">'
        + '<div>'
        + '  <div style="display:flex;justify-content:space-between;align-items:center;font-size:11px;color:var(--color-muted);margin-bottom:6px;">'
        + '    <span style="color:' + schColor + ';font-weight:700;">' + esc(schName) + '</span>'
        + '    <span>' + esc(c.num) + '</span>'
        + '  </div>'
        + '  <div style="font-family:var(--font-serif);font-size:20px;font-weight:700;color:' + schColor + ';margin-bottom:4px;">【 ' + esc(c.name) + ' 】</div>'
        + '  <div style="font-size:11.5px;color:var(--color-gold);font-family:var(--font-serif);margin-bottom:6px;">' + esc(c.master_motto || '') + '</div>'
        + '  <div style="font-size:12px;color:var(--color-ink-light);line-height:1.5;margin-bottom:8px;">' + esc(c.core) + '</div>'
        + '</div>'
        + '<div style="border-top:1px dashed var(--color-border);padding-top:8px;display:flex;justify-content:space-between;align-items:center;font-size:11px;">'
        + '  <span style="color:var(--color-muted);">' + esc(c.series) + '</span>'
        + '  <button class="btn sm" style="padding:2px 8px;font-size:11px;" onclick="selectPantheonCardToConsult(\'' + esc(c.name) + '\', \'' + esc(c.school) + '\')">由此开悟</button>'
        + '</div>'
        + '</div>';
    }).join('');
  }

  function filterPantheonCards(sch, btn) {
    currentPantheonFilter = sch;
    var bar = $('pantheonFilterBar');
    if (bar) {
      var pills = bar.querySelectorAll('.inspo-pill');
      pills.forEach(function(p) { p.classList.remove('active'); });
      if (btn) btn.classList.add('active');
    }
    renderPantheonSection();
  }

  function toggleA4PrintModal(show) {
    var modal = $('modalA4Print');
    if (!modal) return;
    if (show) {
      modal.classList.remove('hidden');
      renderA4SheetCards();
    } else {
      modal.classList.add('hidden');
    }
  }

  function renderA4SheetCards() {
    var sheet = $('a4PrintSheet');
    if (!sheet) return;
    var cards = (window.__WUTANG_DATA__ && window.__WUTANG_DATA__.zenCards108) ? window.__WUTANG_DATA__.zenCards108 : [];
    // 默认选取前9张不同门类的代表卡
    var sample9 = cards.slice(0, 9);
    sheet.innerHTML = sample9.map(function(c) {
      var schColor = (c.school === 'daoism') ? '#2B4C5F' : ((c.school === 'buddhism') ? '#B58900' : '#8E2927');
      return '<div style="border:1.5px solid ' + schColor + ';border-radius:8px;padding:10px;text-align:center;background:#FAF8F2;aspect-ratio:2.5/3.5;display:flex;flex-direction:column;justify-content:space-between;box-sizing:border-box;">'
        + '<div style="font-size:10px;color:var(--color-muted);display:flex;justify-content:space-between;"><span>悟堂·常道</span><span>' + esc(c.num) + '</span></div>'
        + '<div><div style="font-family:var(--font-serif);font-size:24px;font-weight:700;color:' + schColor + ';">【 ' + esc(c.name) + ' 】</div>'
        + '<div style="font-size:11px;color:' + schColor + ';margin-top:2px;">' + esc(c.master) + '</div></div>'
        + '<div style="font-size:10.5px;color:var(--color-ink-light);line-height:1.4;">' + esc(c.core.slice(0, 24)) + '</div>'
        + '<div style="border-top:1px dashed #CCC;padding-top:4px;font-size:9.5px;color:var(--color-muted);">300 DPI 裁切线 63x88mm</div>'
        + '</div>';
    }).join('');
  }

  function selectPantheonCardToConsult(cardName, school) {
    if ($('userTextarea')) {
      $('userTextarea').value = '先圣在上，弟子在【' + cardName + '】一关偶有困惑，求宗师指点迷津...';
      $('userTextarea').dispatchEvent(new Event('input'));
    }
    // 切换到对应流派
    if ($('schoolTrackPills')) {
      var pills = $('schoolTrackPills').querySelectorAll('.school-pill');
      pills.forEach(function(p) {
        if (p.getAttribute('data-track') === school) {
          p.click();
        }
      });
    }
    switchMainTab('relief');
    if ($('userTextarea')) $('userTextarea').focus();
    showToast('已选定【' + cardName + '】心结，正在为您引导至解忧道席');
  }

  function drawRandomPantheonCard() {
    var cards = (window.__WUTANG_DATA__ && window.__WUTANG_DATA__.zenCards108) ? window.__WUTANG_DATA__.zenCards108 : [];
    if (!cards.length) return;
    var idx = Math.floor(Math.random() * cards.length);
    var c = cards[idx];
    selectPantheonCardToConsult(c.name, c.school);
  }


  function renderCardsSection() {
    renderPantheonSection();

    renderZen96CardsSection();

    renderThemePackGrid();

    renderFavoriteCards();

  }



  // ==========================================================================

  // 96 张东方觉察牌（848x1264）画廊、抽卡与解忧融合引擎

  // ==========================================================================

  var currentZen96Filter = '全部';

  var currentZen96ModalCard = null;



  function renderZen96CardsSection() {

    var grid = $('zen96CardsGrid');

    if (!grid) return;

    if (!ZEN_CARDS_96 || !ZEN_CARDS_96.length) {

      grid.innerHTML = '<div style="grid-column:1/-1;text-align:center;padding:20px;color:var(--color-muted);">卡牌资产正在加载...</div>';

      return;

    }



    var list = (currentZen96Filter === '全部') 

      ? ZEN_CARDS_96 

      : ZEN_CARDS_96.filter(function(c) { return c.series === currentZen96Filter; });



    var favList = getStorageJson('wutang_favorite_cards', []);



    grid.innerHTML = list.map(function(c) {

      var isFav = (favList.indexOf(c.card_id) !== -1);

      return '<div class="studio-card-item" style="padding:0;overflow:hidden;border:1px solid #D9CEBD;background:#FAF6EF;display:flex;flex-direction:column;">'

        + '  <div style="width:100%;aspect-ratio:2/3;background:#E8E2D6;overflow:hidden;cursor:pointer;position:relative;" onclick="openZen96CardModal(\'' + c.card_id + '\')">'

        + '    <img src="' + c.image_png + '" alt="' + esc(c.name) + '" loading="lazy" style="width:100%;height:100%;object-fit:cover;transition:transform 0.3s ease;">'

        + '    <div style="position:absolute;bottom:8px;right:8px;background:rgba(42,38,35,0.75);color:#fff;font-size:11px;padding:2px 8px;border-radius:12px;backdrop-filter:blur(4px);">3D 赏析</div>'

        + '  </div>'

        + '  <div style="padding:12px 14px;flex:1;display:flex;flex-direction:column;justify-content:space-between;">'

        + '    <div>'

        + '      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px;">'

        + '        <span class="badge ok" style="font-size:11px;padding:1px 6px;">' + esc(c.series) + ' · ' + c.num + '</span>'

        + '        <button class="btn ghost sm" style="padding:2px 6px;font-size:12px;" onclick="toggleFavoriteCard(\'' + c.card_id + '\')">'

        + (isFav ? '★' : '☆')

        + '        </button>'

        + '      </div>'

        + '      <h4 style="font-family:var(--font-serif);margin:4px 0 6px;font-size:17px;font-weight:bold;">' + esc(c.name) + '</h4>'

        + '      <p style="margin:0 0 8px;font-size:12.5px;color:var(--color-primary);font-family:var(--font-serif);line-height:1.5;">“' + esc(c.core) + '”</p>'

        + '    </div>'

        + '    <button class="btn sm secondary" style="width:100%;margin-top:6px;font-size:12.5px;padding:6px 0;" onclick="openZen96CardModal(\'' + c.card_id + '\')">翻看自省导语</button>'

        + '  </div>'

        + '</div>';

    }).join('');

  }



  window.filterZen96Cards = function(series, btnEl) {

    currentZen96Filter = series;

    var container = $('zen96FilterBar');

    if (container) {

      var btns = container.querySelectorAll('.inspo-pill');

      btns.forEach(function(b) { b.classList.remove('active'); });

      if (btnEl) btnEl.classList.add('active');

    }

    renderZen96CardsSection();

  };



  window.openZen96CardModal = function(cardId) {

    if (!ZEN_CARDS_96 || !ZEN_CARDS_96.length) return;

    var card = ZEN_CARDS_96.find(function(item) { return item.card_id === cardId; });

    if (!card) card = ZEN_CARDS_96[0];

    currentZen96ModalCard = card;



    if ($('zen96ModalSeriesBadge')) $('zen96ModalSeriesBadge').textContent = card.series + ' · ' + card.num;

    if ($('zen96ModalTitle')) $('zen96ModalTitle').textContent = card.name;

    if ($('zen96ModalCore')) $('zen96ModalCore').textContent = '“' + card.core + '”';

    if ($('zen96ModalImg')) $('zen96ModalImg').src = card.image_png;



    if ($('zen96ModalBackTitle')) $('zen96ModalBackTitle').textContent = card.name;

    if ($('zen96ModalBackNum')) $('zen96ModalBackNum').textContent = '【' + card.series + ' · 编号 ' + card.num + '】';

    if ($('zen96ModalBackScene')) $('zen96ModalBackScene').textContent = '画面意境：' + (card.scene || card.core);

    if ($('zen96ModalBackQuestion')) $('zen96ModalBackQuestion').textContent = '💡 觉察问句：' + (card.question || '静观当下，细细觉察此刻的真实发生。');



    var idx = ZEN_CARDS_96.indexOf(card);

    if ($('zen96ModalCounter')) $('zen96ModalCounter').textContent = (idx + 1) + ' / ' + ZEN_CARDS_96.length;



    var favList = getStorageJson('wutang_favorite_cards', []);

    var isFav = (favList.indexOf(card.card_id) !== -1);

    if ($('btnZen96FavToggle')) $('btnZen96FavToggle').textContent = isFav ? '★ 已珍藏' : '☆ 珍藏此卡';



    var flipper = $('zen96ModalFlipper');

    if (flipper) flipper.style.transform = 'rotateY(0deg)';



    var modal = $('zen96Modal');

    if (modal) modal.classList.remove('hidden');

  };



  window.closeZen96Modal = function() {

    var modal = $('zen96Modal');

    if (modal) modal.classList.add('hidden');

  };



  window.toggleZen96ModalFlip = function() {

    var flipper = $('zen96ModalFlipper');

    if (!flipper) return;

    var isFlipped = (flipper.style.transform === 'rotateY(180deg)');

    flipper.style.transform = isFlipped ? 'rotateY(0deg)' : 'rotateY(180deg)';

  };



  window.prevZen96Card = function() {

    if (!currentZen96ModalCard || !ZEN_CARDS_96.length) return;

    var idx = ZEN_CARDS_96.indexOf(currentZen96ModalCard);

    var prevIdx = (idx - 1 + ZEN_CARDS_96.length) % ZEN_CARDS_96.length;

    openZen96CardModal(ZEN_CARDS_96[prevIdx].card_id);

  };



  window.nextZen96Card = function() {

    if (!currentZen96ModalCard || !ZEN_CARDS_96.length) return;

    var idx = ZEN_CARDS_96.indexOf(currentZen96ModalCard);

    var nextIdx = (idx + 1) % ZEN_CARDS_96.length;

    openZen96CardModal(ZEN_CARDS_96[nextIdx].card_id);

  };



  window.drawRandomZen96Card = function() {

    if (!ZEN_CARDS_96 || !ZEN_CARDS_96.length) return;

    var rnd = Math.floor(Math.random() * ZEN_CARDS_96.length);

    openZen96CardModal(ZEN_CARDS_96[rnd].card_id);

  };



  window.toggleZen96ModalFav = function() {

    if (!currentZen96ModalCard) return;

    toggleFavoriteCard(currentZen96ModalCard.card_id);

    var favList = getStorageJson('wutang_favorite_cards', []);

    var isFav = (favList.indexOf(currentZen96ModalCard.card_id) !== -1);

    if ($('btnZen96FavToggle')) $('btnZen96FavToggle').textContent = isFav ? '★ 已珍藏' : '☆ 珍藏此卡';

    renderZen96CardsSection();

  };



  window.useZen96InRelief = function() {

    if (!currentZen96ModalCard) return;

    closeZen96Modal();

    if (typeof switchMainTab === 'function') switchMainTab('relief');

    if (typeof switchClientView === 'function') switchClientView('userHome');

    if ($('entryBtnDirect')) $('entryBtnDirect').click();

    var input = $('userTextarea') || $('userInput');

    if (input) {

      input.value = '抽得东方锦囊【' + currentZen96ModalCard.name + '】（核心智慧：“' + currentZen96ModalCard.core + '”）。想请先贤结合我的近况给予破局指引：\n';

      input.dispatchEvent(new Event('input'));

      input.focus();

    }

    showToast('已将东方锦囊【' + currentZen96ModalCard.name + '】带入解忧处，静候先贤批笺');

  };

  window.switchTab = function(t) { if (typeof switchMainTab === 'function') switchMainTab(t); };







  // --------------------------------------------------------------------------

  // 5. 个人数据与独立隐私授权管理模块 (Mine & Privacy Matrix: F-19 / 10.6)

  // --------------------------------------------------------------------------

  function initDataManagementHandlers() {

    // 导出全量本地数据

    if ($('btnExportAllUserData')) {

      $('btnExportAllUserData').onclick = function() {

        var backup = {

          export_time: new Date().toISOString(),

          version: 'PRD 3.0',

          relief_history: getStorageJson('wutang_relief_history', []),

          mood_checkins: getStorageJson('wutang_mood_checkins', []),

          journals: getStorageJson('wutang_journals', []),

          action_reviews: getStorageJson('wutang_action_reviews', []),

          wellbeing_assessments: getStorageJson('wutang_assessments', []),

          favorite_cards: getStorageJson('wutang_favorite_cards', [])

        };

        var blob = new Blob([JSON.stringify(backup, null, 2)], { type: 'application/json' });

        var a = document.createElement('a');

        a.href = URL.createObjectURL(blob);

        a.download = 'wutang_personal_backup_' + new Date().toISOString().slice(0, 10) + '.json';

        a.click();

        showToast('个人数据包导出完成');

      };

    }



    // 清空本地数据

    if ($('btnClearAllUserData')) {

      $('btnClearAllUserData').onclick = function() {

        if (!confirm('确定彻底清空此设备上的所有悟堂记录（包含解忧历史、日记、签到与自评）吗？此操作无法撤回。')) return;

        ['wutang_relief_history', 'wutang_mood_checkins', 'wutang_journals', 'wutang_action_reviews', 'wutang_assessments', 'wutang_favorite_cards'].forEach(function(k) {

          localStorage.removeItem(k);

        });

        showToast('本地所有记录已彻底清除');

        updateDataSummary();

        renderMineSection();

      };

    }



    // 授权开关监听

    ['consentToggleGrowth', 'consentToggleWellbeing', 'consentTogglePublic'].forEach(function(id) {

      var el = $(id);

      if (el) {

        el.onchange = function() {

          showToast('隐私授权设置已同步');

        };

      }

    });



    updateDataSummary();

  }



  function updateDataSummary() {

    var el = $('dataSummaryNotice');

    if (!el) return;

    var hCount = getStorageJson('wutang_relief_history', []).length;

    var mCount = getStorageJson('wutang_mood_checkins', []).length;

    var jCount = getStorageJson('wutang_journals', []).length;

    var aCount = getStorageJson('wutang_assessments', []).length;

    el.textContent = hCount + ' 条足迹 · ' + mCount + ' 次签到 · ' + jCount + ' 篇日记 · ' + aCount + ' 次自评';

  }





  // ================= 禅意卡牌与书笺画廊渲染 =================

  function renderCardGallery(filter) {

    filter = filter || 'all';

    var container = $('galleryContainer');

    if (!container) return;



    var cards = CARDS_MANIFEST.cards || [];

    var bookmarks = CARDS_MANIFEST.bookmarks || [];



    var html = '';



    // 卡牌过滤

    var showCards = (filter !== 'bookmark');

    var filteredCards = cards;

    if (filter === 'core') {

      filteredCards = cards.filter(function(c) { return c.id.indexOf('card_') === 0; });

    } else if (filter === 'database') {

      filteredCards = cards.filter(function(c) { return c.id.indexOf('cat_') === 0; });

    } else if (filter === 'scenario') {

      filteredCards = cards.filter(function(c) { return c.id.indexOf('scn_') === 0; });

    }



    if (showCards && filteredCards.length > 0) {

      filteredCards.forEach(function(c) {

        var fImg = getCardAsset(c.id, 'front');

        var bImg = getCardAsset(c.id, 'back');

        html += '<div class="gallery-card-item">'

          + '  <div class="gallery-card-3d-wrap" onclick="this.classList.toggle(\'flipped\')" title="点击翻转正反面">'

          + '    <div class="gallery-card-3d-inner">'

          + '      <div class="gallery-card-face face-back" style="background-image:url(\'' + bImg + '\');"></div>'

          + '      <div class="gallery-card-face face-front" style="background-image:url(\'' + fImg + '\');"></div>'

          + '    </div>'

          + '  </div>'

          + '  <div class="gallery-flip-hint">↺ 点击卡面翻转 (正面/反面)</div>'

          + '  <div class="gallery-card-info">'

          + '    <h4>' + esc(c.name) + '</h4>'

          + '    <p>' + esc(c.description) + '</p>'

          + '  </div>'

          + '  <div class="gallery-card-actions">'

          + '    <a href="' + fImg + '" download="' + c.id + '_front.png" class="btn sm ghost" style="text-decoration:none;font-size:11px;padding:3px 8px;">下载正面</a>'

          + '    <a href="' + bImg + '" download="' + c.id + '_back.png" class="btn sm secondary" style="text-decoration:none;font-size:11px;padding:3px 8px;">下载背面</a>'

          + '  </div>'

          + '</div>';

      });

    }



    // 书笺过滤

    var showBookmarks = (filter === 'all' || filter === 'bookmark');

    if (showBookmarks && bookmarks.length > 0) {

      bookmarks.forEach(function(b) {

        var bmImg = getBookmarkAsset(b.id);

        html += '<div class="gallery-bm-item">'

          + '  <img src="' + bmImg + '" alt="' + esc(b.name) + '" class="gallery-bm-img">'

          + '  <div class="gallery-card-info">'

          + '    <h4>' + esc(b.name) + '</h4>'

          + '    <p>' + esc(b.description) + '</p>'

          + '  </div>'

          + '  <div class="gallery-card-actions">'

          + '    <a href="' + bmImg + '" download="' + b.id + '.png" class="btn sm" style="text-decoration:none;font-size:12px;padding:4px 14px;">下载书笺 PNG</a>'

          + '  </div>'

          + '</div>';

      });

    }



    container.innerHTML = html || '<div style="grid-column:1/-1;padding:40px;text-align:center;color:var(--color-muted);">暂无匹配项目</div>';

  }



  

  // ==========================================================================

  // 悟堂 · 禅意背景音乐控制引擎 (Zen Ambient Background Music Engine)

  // 包含《Flowing Mind 行云流水》与《Zen Meditation 禅境冥想》两首东方禅意音轨

  // ==========================================================================

  var bgmEngine = (function() {

    var TRACKS = [

      {

        id: 'flowing_mind',

        name: '行云流水',

        subtitle: 'Flowing Mind',

        src: 'assets/audio/flowing_mind.m4a',

        fallbackSrc: 'assets/audio/Flowing Mind.m4a',

        desc: '空灵澄澈 · 清心释压'

      },

      {

        id: 'zen_meditation',

        name: '禅境冥想',

        subtitle: 'Zen Meditation',

        src: 'assets/audio/zen_meditation.m4a',

        fallbackSrc: 'assets/audio/Zen Meditation.m4a',

        desc: '沉静幽远 · 凝神入定'

      }

    ];



    var currentIndex = 0;

    var isPlaying = false;

    var volume = 0.35; // 默认 35% 舒适背景音量

    var audio = null;

    var isPanelOpen = false;



    function init() {

      audio = $('bgmAudio');

      if (!audio) {

        audio = new Audio();

        audio.id = 'bgmAudio';

        audio.preload = 'auto';

        document.body.appendChild(audio);

      }



      // 读取本地持久化偏好

      try {

        var saved = localStorage.getItem('wutang_bgm_pref');

        if (saved) {

          var pref = JSON.parse(saved);

          if (typeof pref.volume === 'number') volume = Math.max(0, Math.min(1, pref.volume));

          if (typeof pref.currentIndex === 'number' && pref.currentIndex >= 0 && pref.currentIndex < TRACKS.length) {

            currentIndex = pref.currentIndex;

          }

        }

      } catch (e) {}



      audio.volume = volume;

      loadTrack(currentIndex, false);



      // 事件监听

      audio.addEventListener('ended', function() {

        nextTrack(true);

      });



      audio.addEventListener('play', function() {

        isPlaying = true;

        updateUI();

      });



      audio.addEventListener('pause', function() {

        isPlaying = false;

        updateUI();

      });



      audio.addEventListener('error', function() {

        var track = TRACKS[currentIndex];

        if (track && track.fallbackSrc && audio.src !== track.fallbackSrc) {

          audio.src = track.fallbackSrc;

          if (isPlaying) {

            audio.play().catch(function() {});

          }

        }

      });



      renderTrackList();

      updateUI();

      setupBgmEvents();

    }



    function savePref() {

      try {

        localStorage.setItem('wutang_bgm_pref', JSON.stringify({

          volume: volume,

          currentIndex: currentIndex

        }));

      } catch (e) {}

    }



    function loadTrack(index, autoPlay) {

      if (index < 0 || index >= TRACKS.length) index = 0;

      currentIndex = index;

      var track = TRACKS[currentIndex];

      audio.src = track.src;

      savePref();

      renderTrackList();

      updateUI();



      if (autoPlay) {

        play();

      }

    }



    function play() {

      if (!audio.src) {

        audio.src = TRACKS[currentIndex].src;

      }

      var promise = audio.play();

      if (promise !== undefined) {

        promise.then(function() {

          isPlaying = true;

          updateUI();

        }).catch(function(err) {

          console.warn('[BGM] 浏览器自动播放拦截或音频加载未完成:', err);

          isPlaying = false;

          updateUI();

          if (typeof showToast === 'function') {

            showToast('请轻触屏幕以开启背景音乐');

          }

        });

      }

    }



    function pause() {

      audio.pause();

      isPlaying = false;

      updateUI();

    }



    function togglePlay() {

      if (isPlaying) {

        pause();

      } else {

        play();

      }

    }



    function nextTrack(autoPlay) {

      var nextIdx = (currentIndex + 1) % TRACKS.length;

      loadTrack(nextIdx, autoPlay !== false);

    }



    function prevTrack(autoPlay) {

      var prevIdx = (currentIndex - 1 + TRACKS.length) % TRACKS.length;

      loadTrack(prevIdx, autoPlay !== false);

    }



    function setVolume(val) {

      volume = Math.max(0, Math.min(1, val));

      if (audio) audio.volume = volume;

      savePref();

      updateUI();

    }



    function renderTrackList() {

      var listEl = $('bgmTrackList');

      if (!listEl) return;

      var html = '';

      TRACKS.forEach(function(t, idx) {

        var isActive = (idx === currentIndex);

        html += '<div class="bgm-track-item ' + (isActive ? 'active' : '') + '" data-index="' + idx + '">'

          + '  <div class="bgm-track-info">'

          + '    <div style="display:flex;align-items:center;gap:6px;">'

          + '      <span style="font-size:12px;">' + (isActive && isPlaying ? '🔊' : (isActive ? '🎵' : '⚪')) + '</span>'

          + '      <strong style="font-size:13px;">' + esc(t.name) + '</strong>'

          + '      <span style="font-size:11px;color:var(--color-muted);">' + esc(t.subtitle) + '</span>'

          + '    </div>'

          + '    <span class="bgm-track-sub">' + esc(t.desc) + '</span>'

          + '  </div>'

          + '  <div style="font-size:11px;color:' + (isActive ? 'var(--color-primary)' : 'var(--color-muted)') + ';">'

          + (isActive && isPlaying ? '播放中' : (isActive ? '已选' : '播放'))

          + '  </div>'

          + '</div>';

      });

      listEl.innerHTML = html;



      // 绑定曲目点击

      var items = listEl.querySelectorAll('.bgm-track-item');

      items.forEach(function(item) {

        item.addEventListener('click', function(e) {

          e.stopPropagation();

          var idx = parseInt(item.getAttribute('data-index'), 10);

          if (idx === currentIndex && isPlaying) {

            pause();

          } else {

            loadTrack(idx, true);

          }

        });

      });

    }



    function updateUI() {

      var curTrack = TRACKS[currentIndex] || TRACKS[0];

      var toggleBtn = $('btnBgmToggle');

      var statusText = $('bgmStatusText');

      var playPauseBtn = $('btnBgmPlayPause');

      var floatingPill = $('bgmFloatingPill');

      var floatingText = $('bgmFloatingText');

      var volSlider = $('bgmVolumeSlider');

      var volVal = $('bgmVolVal');

      var volIcon = $('bgmVolIcon');



      if (toggleBtn) {

        if (isPlaying) {

          toggleBtn.classList.add('is-playing');

          toggleBtn.title = '背景音乐播放中: ' + curTrack.name + ' (' + curTrack.subtitle + ') · 点击暂停';

        } else {

          toggleBtn.classList.remove('is-playing');

          toggleBtn.title = '背景音乐已暂停 · 点击播放 ' + curTrack.name;

        }

      }



      if (statusText) {

        statusText.textContent = isPlaying ? ('正在播放: ' + curTrack.name) : '静心音乐: 关';

      }



      if (playPauseBtn) {

        playPauseBtn.textContent = isPlaying ? '⏸ 暂停' : '▶ 播放';

      }



      if (floatingPill) {

        if (isPlaying) {

          floatingPill.classList.add('is-playing');

          floatingPill.title = '当前播放: ' + curTrack.name + ' · 点击暂停，双击设置';

        } else {

          floatingPill.classList.remove('is-playing');

          floatingPill.title = '静心音乐已暂停 · 点击播放 ' + curTrack.name;

        }

      }



      if (floatingText) {

        floatingText.textContent = isPlaying ? ('♫ ' + curTrack.name) : '静心音乐: 关';

      }



      if (volSlider) {

        var pct = Math.round(volume * 100);

        volSlider.value = pct;

        if (volVal) volVal.textContent = pct + '%';

        if (volIcon) {

          volIcon.textContent = volume === 0 ? '🔇' : (volume < 0.5 ? '🔉' : '🔊');

        }

      }

    }



    function togglePanel(e) {

      if (e) e.stopPropagation();

      var panel = $('bgmPanel');

      if (!panel) return;

      isPanelOpen = !isPanelOpen;

      if (isPanelOpen) {

        panel.classList.add('show');

        renderTrackList();

      } else {

        panel.classList.remove('show');

      }

    }



    function closePanel() {

      var panel = $('bgmPanel');

      if (panel) {

        panel.classList.remove('show');

        isPanelOpen = false;

      }

    }



    function setupBgmEvents() {

      var btnToggle = $('btnBgmToggle');

      var btnMenuArrow = $('btnBgmMenuArrow');

      var btnPlayPause = $('btnBgmPlayPause');

      var btnPrev = $('btnBgmPrev');

      var btnNext = $('btnBgmNext');

      var btnClose = $('bgmClosePanel');

      var volSlider = $('bgmVolumeSlider');

      var volIcon = $('bgmVolIcon');

      var floatingPill = $('bgmFloatingPill');

      var panel = $('bgmPanel');



      // 点击主按钮主体：开关播放/暂停

      if (btnToggle) {

        btnToggle.addEventListener('click', function(e) {

          if (e.target && e.target.id === 'btnBgmMenuArrow') {

            togglePanel(e);

            return;

          }

          togglePlay();

        });

      }



      if (btnMenuArrow) {

        btnMenuArrow.addEventListener('click', function(e) {

          togglePanel(e);

        });

      }



      if (floatingPill) {

        floatingPill.addEventListener('click', function() {

          togglePlay();

        });

      }



      if (btnPlayPause) {

        btnPlayPause.addEventListener('click', function(e) {

          e.stopPropagation();

          togglePlay();

        });

      }



      if (btnPrev) {

        btnPrev.addEventListener('click', function(e) {

          e.stopPropagation();

          prevTrack(true);

        });

      }



      if (btnNext) {

        btnNext.addEventListener('click', function(e) {

          e.stopPropagation();

          nextTrack(true);

        });

      }



      if (btnClose) {

        btnClose.addEventListener('click', function(e) {

          e.stopPropagation();

          closePanel();

        });

      }



      if (volSlider) {

        volSlider.addEventListener('input', function(e) {

          e.stopPropagation();

          var val = parseFloat(volSlider.value) / 100;

          setVolume(val);

        });

      }



      if (volIcon) {

        volIcon.addEventListener('click', function(e) {

          e.stopPropagation();

          if (volume > 0) {

            volIcon.setAttribute('data-last-vol', volume);

            setVolume(0);

          } else {

            var last = parseFloat(volIcon.getAttribute('data-last-vol') || '0.35');

            setVolume(last || 0.35);

          }

        });

      }



      // 点击外部自动收起面板

      document.addEventListener('click', function(e) {

        if (!panel || !isPanelOpen) return;

        var wrap = $('bgmControlWrap');

        if (wrap && !wrap.contains(e.target)) {

          closePanel();

        }

      });



      // 阻止面板内部点击冒泡

      if (panel) {

        panel.addEventListener('click', function(e) {

          e.stopPropagation();

        });

      }

    }



    return {

      init: init,

      play: play,

      pause: pause,

      togglePlay: togglePlay,

      nextTrack: nextTrack,

      prevTrack: prevTrack,

      setVolume: setVolume,

      togglePanel: togglePanel,

      closePanel: closePanel

    };

  })();



// 启动初始化

  function bootstrap() {

    initScenarioChips();

    setupEvents();

    renderClassicsList();

    var totalCards = (CARDS_MINDSET && CARDS_MINDSET.length) ? CARDS_MINDSET.length : 16;

    appState.awarenessIndex = Math.floor(Math.random() * totalCards);

    renderAwarenessCard(appState.awarenessIndex);

    renderStudioCards('all');

    lotusEngine.init('lotusCanvas');

    updateManagerUI();

    checkAiBackendStatus();

    bgmEngine.init();

    // PRD 3.0 新增模块初始化

    initGrowthModule();

    initWellbeingModule();

    initPracticeModule();

    initCardsModule();

    initDataManagementHandlers();

  }



  if (document.readyState === 'loading') {

    document.addEventListener('DOMContentLoaded', bootstrap);

  } else {

    bootstrap();

  }



})();

