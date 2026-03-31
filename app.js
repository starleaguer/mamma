// ===== RECIPE DATABASE =====

if ("serviceWorker" in navigator) {
  navigator.serviceWorker.register("/service-worker.js");
}

const DEFAULT_RECIPES = [
  {
    id: 1, emoji: '🍚', name: '닭고기 야채죽',
    age: '10개월+', time: '30분', difficulty: '쉬움',
    ingredients: ['쌀', '닭고기', '당근', '애호박', '양파'],
    description: '부드러운 닭고기와 달콤한 야채가 어우러진 영양 가득 죽',
    steps: [
      '쌀은 30분 이상 물에 불려 두세요.',
      '닭고기는 삶아서 잘게 찢어두세요.',
      '당근, 애호박, 양파는 곱게 다져주세요.',
      '냄비에 불린 쌀과 닭 육수를 넣고 중불에서 끓이세요.',
      '쌀이 퍼지면 손질한 야채와 닭고기를 넣어 저어가며 끓이세요.',
      '걸쭉해지면 완성입니다. 소금 없이 담백하게 드세요.',
    ],
    tip: '닭 육수 대신 물로만 끓여도 돼요. 야채를 더 작게 다지면 10개월 아기도 잘 먹어요.',
  },
  {
    id: 2, emoji: '🥕', name: '당근 달걀찜',
    age: '6개월+', time: '20분', difficulty: '쉬움',
    ingredients: ['당근', '달걀', '육수'],
    description: '촉촉하고 부드러운 식감으로 이유식 초기 아기도 OK',
    steps: [
      '당근은 쪄서 곱게 갈아주세요.',
      '달걀을 풀어 채에 걸러 부드럽게 만드세요.',
      '달걀물에 갈아둔 당근과 육수를 넣고 잘 섞으세요.',
      '그릇에 담아 랩을 씌우고 전자레인지에 3분, 또는 찜기에 10분 쪄주세요.',
      '표면이 말끔히 굳으면 완성이에요.',
    ],
    tip: '뚜껑이나 랩으로 덮어서 쪄야 수분이 날아가지 않고 촉촉해져요.',
  },
  {
    id: 3, emoji: '🥦', name: '브로콜리 두부 무침',
    age: '12개월+', time: '15분', difficulty: '쉬움',
    ingredients: ['브로콜리', '두부', '참기름', '간장'],
    description: '단백질과 비타민이 풍부한 간편 반찬',
    steps: [
      '브로콜리는 끓는 물에 2분 데쳐 잘게 다져주세요.',
      '두부는 찬물에 씻어 면포로 물기를 꼭 짜세요.',
      '두부를 으깨고 브로콜리와 합쳐주세요.',
      '아기 간장 1/2 작은술, 참기름 한 방울 넣고 고루 섞으세요.',
    ],
    tip: '24개월 미만 아기는 간장과 참기름 양을 아주 소량만 사용하세요.',
  },
  {
    id: 4, emoji: '🍠', name: '고구마 팬케이크',
    age: '12개월+', time: '25분', difficulty: '보통',
    ingredients: ['고구마', '달걀', '쌀가루', '바나나'],
    description: '달콤한 고구마와 바나나로 만든 건강 간식 팬케이크',
    steps: [
      '고구마는 쪄서 껍질을 벗기고 으깨주세요.',
      '바나나도 포크로 곱게 으깨주세요.',
      '달걀, 쌀가루를 함께 넣고 잘 섞어 반죽을 만드세요.',
      '팬에 오일을 살짝 두르고 반죽을 떠서 약불로 노릇하게 굽세요.',
      '앞뒤로 뒤집어 익히면 완성!',
    ],
    tip: '쌀가루 대신 일반 밀가루를 써도 돼요. 반죽이 너무 묽으면 쌀가루를 조금 더 추가하세요.',
  },
  {
    id: 5, emoji: '🥔', name: '감자 수프',
    age: '9개월+', time: '25분', difficulty: '쉬움',
    ingredients: ['감자', '양파', '당근', '우유', '버터'],
    description: '크리미하고 달달한 감자 수프, 국물 이유식에 딱!',
    steps: [
      '감자, 당근, 양파를 껍질 벗겨 작게 썰어주세요.',
      '냄비에 버터를 녹이고 양파를 투명해질 때까지 볶아주세요.',
      '감자와 당근을 넣고 물을 자박하게 부어 20분 끓이세요.',
      '재료가 충분히 익으면 블렌더로 갈아주세요.',
      '우유를 넣고 농도를 조절한 후 한번 더 끓이면 완성!',
    ],
    tip: '우유 알레르기가 있는 경우 두유나 코코넛 밀크로 대체하세요.',
  },
  {
    id: 6, emoji: '🍳', name: '달걀 야채 볶음밥',
    age: '18개월+', time: '20분', difficulty: '쉬움',
    ingredients: ['달걀', '당근', '애호박', '쌀', '양파', '간장'],
    description: '냉장고 남은 야채를 모두 활용하는 만능 볶음밥',
    steps: [
      '당근, 애호박, 양파를 잘게 다져주세요.',
      '팬에 오일을 두르고 야채를 볶아주세요.',
      '밥을 넣고 함께 볶다가 달걀을 풀어 넣으세요.',
      '간장 1/2 작은술로 살짝 간하며 볶아주면 완성!',
    ],
    tip: '야채를 충분히 볶아야 단맛이 나요. 참기름을 한 방울 떨어뜨리면 향이 좋아져요.',
  },
  {
    id: 7, emoji: '🥩', name: '소고기 무국',
    age: '9개월+', time: '35분', difficulty: '보통',
    ingredients: ['소고기', '무', '달걀', '국간장', '파'],
    description: '구수하고 개운한 소고기 무국, 한식 대표 아기 국물 요리',
    steps: [
      '소고기는 핏물을 빼고 작게 썰어주세요.',
      '무는 깍둑썰기 해주세요.',
      '냄비에 기름을 두르고 소고기를 볶다가 무를 넣어 함께 볶아요.',
      '물을 넉넉히 붓고 20분 이상 푹 끓여주세요.',
      '아기 국간장으로 살짝 간해주세요.',
    ],
    tip: '소고기를 먼저 잘 볶아야 구수한 맛이 나요. 파는 돌 이후에 소량 넣을 수 있어요.',
  },
  {
    id: 8, emoji: '🍜', name: '닭고기 우동',
    age: '18개월+', time: '20분', difficulty: '쉬움',
    ingredients: ['닭고기', '우동면', '당근', '애호박', '육수'],
    description: '쫄깃한 우동면과 부드러운 닭고기의 만남',
    steps: [
      '닭고기는 삶아서 잘게 찢어주세요.',
      '당근과 애호박은 편으로 썰어주세요.',
      '육수(또는 물)를 끓이다가 야채와 닭고기를 넣으세요.',
      '우동면을 넣고 3-4분 더 끓이면 완성!',
    ],
    tip: '아기용으로는 면을 짧게 잘라주면 먹기 편해요. 육수는 시판 아기 육수나 집에서 낸 닭 육수를 사용하세요.',
  },
  {
    id: 9, emoji: '🥗', name: '두부 달걀 구이',
    age: '10개월+', time: '15분', difficulty: '쉬움',
    ingredients: ['두부', '달걀', '당근', '파프리카'],
    description: '단백질 풍부한 두부와 달걀의 조합, 간식으로도 OK',
    steps: [
      '두부는 물기를 제거하고 으깨주세요.',
      '당근과 파프리카는 곱게 다져주세요.',
      '두부, 달걀, 야채를 모두 섞어 반죽하세요.',
      '팬에 오일을 두르고 한 숟가락씩 떠서 납작하게 눌러 굽세요.',
      '앞뒤로 노릇하게 구우면 완성!',
    ],
    tip: '모양틀을 이용하면 귀여운 모양으로 만들 수 있어요. 케첩을 살짝 찍어먹으면 더 맛있어요.',
  },
  {
    id: 10, emoji: '🍲', name: '시금치 된장국',
    age: '12개월+', time: '15분', difficulty: '쉬움',
    ingredients: ['시금치', '된장', '두부', '육수', '파'],
    description: '철분 풍부한 시금치로 만든 영양 된장국',
    steps: [
      '시금치는 끓는 물에 살짝 데쳐 물기를 짜고 2cm 길이로 썰어주세요.',
      '두부는 작게 깍둑썰기 해주세요.',
      '육수에 된장을 풀어 넣고 끓이세요.',
      '두부와 시금치를 넣고 5분 더 끓이면 완성!',
    ],
    tip: '아기 된장을 사용하거나 일반 된장은 소량만 쓰세요. 간은 최소화해야 해요.',
  },
  {
    id: 11, emoji: '🥞', name: '바나나 오트밀 팬케이크',
    age: '12개월+', time: '20분', difficulty: '쉬움',
    ingredients: ['바나나', '달걀', '오트밀', '우유'],
    description: '밀가루 없이 만드는 글루텐 프리 건강 팬케이크',
    steps: [
      '바나나를 포크로 으깨주세요.',
      '오트밀은 블렌더로 곱게 갈아주세요.',
      '바나나, 달걀, 오트밀 가루, 우유를 잘 섞어 반죽하세요.',
      '팬에 오일을 두르고 반죽을 떠서 약불로 구워주세요.',
      '기포가 생기면 뒤집어 익히면 완성!',
    ],
    tip: '바나나가 달콤하기 때문에 설탕은 전혀 넣지 않아도 맛있어요!',
  },
  {
    id: 12, emoji: '🐟', name: '흰살 생선 야채죽',
    age: '9개월+', time: '30분', difficulty: '보통',
    ingredients: ['쌀', '흰살생선', '당근', '브로콜리', '육수'],
    description: '오메가3 풍부한 생선과 영양 야채의 완벽한 이유식',
    steps: [
      '쌀은 미리 불려두세요.',
      '흰살생선(대구, 가자미 등)은 쪄서 잘게 으깨주세요.',
      '당근과 브로콜리는 잘게 다져주세요.',
      '냄비에 불린 쌀과 육수를 넣고 끓이세요.',
      '야채와 생선을 추가하여 걸쭉하게 끓이면 완성!',
    ],
    tip: '생선 가시를 완벽히 제거하는 것이 중요해요. 쪄서 손으로 꼼꼼히 확인하세요.',
  },
  {
    id: 13, emoji: '🧆', name: '소고기 완자',
    age: '12개월+', time: '25분', difficulty: '보통',
    ingredients: ['소고기', '두부', '당근', '달걀', '전분'],
    description: '부드럽고 쫄깃한 소고기 두부 완자, 간식으로도 좋아요',
    steps: [
      '소고기는 다져주세요.',
      '두부는 물기를 제거하고 으깨주세요.',
      '당근은 곱게 다져주세요.',
      '소고기, 두부, 당근, 달걀, 전분을 넣고 잘 치대주세요.',
      '한 입 크기로 둥글게 빚어 팬에 올려 굽거나 찜기에 쪄주세요.',
    ],
    tip: '냉동 보관했다가 필요할 때 꺼내 먹이면 편해요. 케첩을 살짝 찍어줘도 좋아요.',
  },
  {
    id: 14, emoji: '🥛', name: '고구마 라떼',
    age: '12개월+', time: '10분', difficulty: '쉬움',
    ingredients: ['고구마', '우유', '꿀'],
    description: '달콤하고 영양 가득한 아이 간식 음료',
    steps: [
      '고구마를 쪄서 껍질을 제거하고 잘 으깨주세요.',
      '우유를 따뜻하게 데워주세요.',
      '블렌더에 고구마와 우유를 넣고 곱게 갈아주세요.',
      '컵에 담아 꿀을 살짝 넣으면 완성!',
    ],
    tip: '꿀은 12개월 미만은 절대 주지 마세요. 그 이전에는 설탕도 쓰지 않는 게 좋아요.',
  },
  {
    id: 15, emoji: '🍙', name: '참치 야채 주먹밥',
    age: '15개월+', time: '15분', difficulty: '쉬움',
    ingredients: ['쌀', '참치', '당근', '오이', '참기름'],
    description: '아이 스스로 집어먹기 좋은 귀여운 주먹밥',
    steps: [
      '당근과 오이는 잘게 다져주세요.',
      '참치는 기름을 빼고 키친타월로 눌러 물기를 제거하세요.',
      '따뜻한 밥에 야채, 참치, 참기름을 넣고 잘 섞어주세요.',
      '한 입 크기로 동글게 빚으면 완성!',
    ],
    tip: '손에 물을 살짝 묻히면 주먹밥이 예쁘게 만들어져요. 김으로 감싸줘도 좋아요.',
  },
  {
    id: 16, emoji: '🥬', name: '시금치 달걀 볶음',
    age: '15개월+', time: '10분', difficulty: '쉬움',
    ingredients: ['시금치', '달걀', '간장', '참기름'],
    description: '간단하지만 영양 만점인 시금치 달걀 볶음 반찬',
    steps: [
      '시금치는 끓는 물에 데쳐 물기를 짜고 3cm 길이로 썰어주세요.',
      '달걀을 풀어두세요.',
      '팬에 오일을 두르고 시금치를 먼저 볶아주세요.',
      '달걀을 부어 스크램블 상태로 함께 볶아주세요.',
      '아기 간장 한 방울, 참기름 한 방울로 마무리!',
    ],
    tip: '시금치를 너무 오래 익히면 영양소가 파괴돼요. 살짝 볶는 것이 포인트예요.',
  },
  {
    id: 17, emoji: '🍖', name: '닭고기 양배추 볶음',
    age: '15개월+', time: '20분', difficulty: '쉬움',
    ingredients: ['닭고기', '양배추', '당근', '간장', '참기름'],
    description: '소화가 잘되는 양배추와 닭고기의 든든한 반찬',
    steps: [
      '닭고기는 잘게 다져주세요.',
      '양배추와 당근은 채 썰어주세요.',
      '팬에 오일을 두르고 닭고기부터 볶아주세요.',
      '당근을 넣어 볶다가 양배추를 마지막에 넣어 볶아주세요.',
      '간장으로 살짝 간하고 참기름으로 마무리!',
    ],
    tip: '양배추는 마지막에 넣어야 아삭한 식감이 살아요.',
  },
  {
    id: 18, emoji: '🫕', name: '두부 순두부찌개',
    age: '18개월+', time: '20분', difficulty: '쉬움',
    ingredients: ['두부', '소고기', '달걀', '애호박', '육수'],
    description: '맵지 않은 담백한 아기 순두부찌개',
    steps: [
      '소고기는 잘게 다져주세요.',
      '애호박은 반달 모양으로 썰어주세요.',
      '냄비에 소고기를 볶다가 육수를 붓고 끓이세요.',
      '순두부를 숟가락으로 떠먹고 애호박을 넣어주세요.',
      '달걀을 풀어 넣고 한번 더 끓이면 완성!',
    ],
    tip: '고춧가루는 절대 넣지 마세요. 담백하게 먹는 것이 아기에게 좋아요.',
  },
];

// ===== SUPABASE CLIENT =====
const { createClient } = supabase;
const SUPABASE_URL = 'https://nvraninnkutvebdgnlfv.supabase.co';
const SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im52cmFuaW5ua3V0dmViZGdubGZ2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzQzNTgzMDcsImV4cCI6MjA4OTkzNDMwN30.wH1ewf0ArHsOTeulFdhAcHrWM18_Fh9SooSJtUNCYUI';
const supabaseClient = createClient(SUPABASE_URL, SUPABASE_KEY);

// Helper to normalize image URLs by removing the base URL
const BASE_URL = 'https://mamma-blond.vercel.app';
function normalizeImageUrl(url) {
  if (!url) return '';
  return url.replace(BASE_URL, '').trim();
}

// Global State for Recipes
let RECIPES = [];

// Initialize App: Fetch from Supabase
async function initApp() {
  const { data, error } = await supabaseClient
    .from('recipes')
    .select('*')
    .order('created_at', { ascending: false });

  if (error) {
    console.error('Supabase fetch error:', error);
    // Fallback to defaults or localstorage if supabase fails
    RECIPES = JSON.parse(localStorage.getItem('myRecipes')) || DEFAULT_RECIPES;
    return;
  }

  if (data && data.length > 0) {
    RECIPES = data;
  } else {
    // If Supabase table is empty, insert default recipes
    console.log('No recipes found in Supabase. Inserting default recipes...');
    const { error: insertError } = await supabaseClient
      .from('recipes')
      .insert(DEFAULT_RECIPES);

    if (insertError) {
      console.error('Error inserting defaults:', insertError);
      RECIPES = DEFAULT_RECIPES;
    } else {
      RECIPES = DEFAULT_RECIPES;
    }
  }
}

// Kick off initialization
initApp();

// ===== STATE =====
let currentKeywords = [];
let selectedModal = null;

const DEFAULT_TAGS = [
  { value: '쌀가루', label: '🌾 쌀가루' },
  { value: '달걀', label: '🥚 달걀' },
  { value: '분유', label: '🍼 분유' },
  { value: '고구마', label: '🍠 고구마' },
  { value: '버터', label: '🧈 버터' },
  { value: '양파', label: '🧅 양파' },
  { value: '오트밀', label: '🥣 오트밀' },
  { value: '바나나', label: '🍌 바나나' },
  { value: '닭고기', label: '🍗 닭고기' },
  { value: '시금치', label: '🥬 시금치' }
];

// Check if we need to update/reset tags to new defaults (one-time migration for old users)
let popularTagsStored = localStorage.getItem('popularTags');
if (popularTagsStored) {
  const parsed = JSON.parse(popularTagsStored);
  // Simple check: if '쌀가루' isn't the first tag, and it was '당근' before, reset it.
  if (parsed.length > 0 && parsed[0].value === '당근') {
    console.log('Migrating popular tags to new defaults based on DB frequency...');
    localStorage.setItem('popularTags', JSON.stringify(DEFAULT_TAGS));
    popularTagsStored = JSON.stringify(DEFAULT_TAGS);
  }
}

let popularTags = popularTagsStored ? JSON.parse(popularTagsStored) : DEFAULT_TAGS;
let tempEditTags = [];

// ===== DOM =====
const searchInput = document.getElementById('searchInput');
const searchBtn = document.getElementById('searchBtn');
const viewAllBtn = document.getElementById('viewAllBtn');
const clearBtn = document.getElementById('clearBtn');
const recipeGrid = document.getElementById('recipeGrid');
const resultsSection = document.getElementById('resultsSection');
const resultsHeader = document.getElementById('resultsHeader');
const resultsTitle = document.getElementById('resultsTitle');
const resultsCount = document.getElementById('resultsCount');
const emptyState = document.getElementById('emptyState');
const initialState = document.getElementById('initialState');
const recipeModal = document.getElementById('recipeModal');
const modalClose = document.getElementById('modalClose');
const editBtn = document.getElementById('editBtn');
const deleteBtn = document.getElementById('deleteBtn');
const modalSteps = document.getElementById('modalSteps');

// Add Recipe Modal
const addRecipeBtn = document.getElementById('addRecipeBtn');
const addRecipeModal = document.getElementById('addRecipeModal');
const addModalClose = document.getElementById('addModalClose');
const addModalCancel = document.getElementById('addModalCancel');
const addRecipeForm = document.getElementById('addRecipeForm');

const formModalTitle = document.getElementById('formModalTitle');
const formModalSubtitle = document.getElementById('formModalSubtitle');
const formSubmitBtn = document.getElementById('formSubmitBtn');

let editingRecipeId = null;

// Edit Tags Modal DOM
const editTagsBtn = document.getElementById('editTagsBtn');
const popularTagsContainer = document.getElementById('popularTags');
const editTagsModal = document.getElementById('editTagsModal');
const editTagsClose = document.getElementById('editTagsClose');
const editTagsCancel = document.getElementById('editTagsCancel');
const saveTagsBtn = document.getElementById('saveTagsBtn');
const newTagInput = document.getElementById('newTagInput');
const addTagBtn = document.getElementById('addTagBtn');
const editTagsList = document.getElementById('editTagsList');

// ===== SEARCH LOGIC =====
function normalize(str) {
  return str.trim().toLowerCase().replace(/\s+/g, '');
}

function matchRecipe(recipe, keywords) {
  const matched = [];
  const normalizedName = normalize(recipe.name);

  for (const kw of keywords) {
    const n = normalize(kw);
    if (!n) continue;

    // Check Name OR Ingredients
    const isNameMatch = normalizedName.includes(n) || n.includes(normalizedName);
    const isIngredientMatch = recipe.ingredients.some(ing => 
      normalize(ing).includes(n) || n.includes(normalize(ing))
    );

    if (isNameMatch || isIngredientMatch) {
      matched.push(kw);
    }
  }
  return matched;
}

function search() {
  const raw = searchInput.value.trim();
  
  if (!raw) {
    // If input is empty, reset to initial state
    currentKeywords = [];
    recipeGrid.innerHTML = '';
    resultsHeader.classList.add('hidden');
    emptyState.classList.add('hidden');
    initialState.classList.remove('hidden');
    syncTagsWithInput();
    return;
  }

  // Parse keywords: split by commas OR spaces
  const keywords = raw.split(/[,，\s]+/).map(k => k.trim()).filter(Boolean);
  currentKeywords = keywords;

  const results = [];
  for (const recipe of RECIPES) {
    const matched = matchRecipe(recipe, keywords);
    // AND search: all keywords must match
    if (matched.length === keywords.length) {
      results.push({ recipe, matched });
    }
  }

  // Sort by name
  results.sort((a, b) => a.recipe.name.localeCompare(b.recipe.name));

  renderResults(results, raw);
  syncTagsWithInput(); // Ensure tags are updated visually
}

// Debounce helper
let searchTimeout = null;
function handleLiveSearch() {
  if (searchTimeout) clearTimeout(searchTimeout);
  searchTimeout = setTimeout(() => {
    search();
  }, 250);
}

// ===== RENDER =====
function renderResults(results, query) {
  recipeGrid.innerHTML = '';
  initialState.classList.add('hidden');

  if (results.length === 0) {
    resultsHeader.classList.add('hidden');
    emptyState.classList.remove('hidden');
    return;
  }

  emptyState.classList.add('hidden');
  resultsHeader.classList.remove('hidden');
  resultsTitle.textContent = `"${query}" 검색 결과`;
  resultsCount.textContent = `${results.length}개 레시피`;

  results.forEach(({ recipe, matched }, idx) => {
    const card = createCard(recipe, matched, idx);
    recipeGrid.appendChild(card);
  });
}

function createCard(recipe, matchedKeywords, idx) {
  const div = document.createElement('div');
  div.className = 'recipe-card';
  div.style.animationDelay = `${idx * 0.07}s`;
  div.setAttribute('role', 'button');
  div.setAttribute('tabindex', '0');
  div.setAttribute('aria-label', recipe.name + ' 레시피 보기');
  div.dataset.recipeId = String(recipe.id);
  
  // Image Background if exists
  let imageHTML = '';
  if (recipe.image_url) {
    const displayUrl = normalizeImageUrl(recipe.image_url);
    imageHTML = `
      <div class="card-image-wrapper">
        <img src="${displayUrl}" alt="${recipe.name}" onerror="this.parentElement.style.display='none'" />
      </div>
    `;
  }

  const tagHTML = recipe.ingredients.map(ing => {
    const isMatch = matchedKeywords.some(kw =>
      normalize(ing).includes(normalize(kw)) || normalize(kw).includes(normalize(ing))
    );
    return `<span class="card-tag ${isMatch ? 'matched' : 'normal'}">${ing}</span>`;
  }).join('');

  let diffBg = 'rgba(255,215,0,0.15)', diffColor = '#ffd700', diffBorder = 'rgba(255,215,0,0.3)'; // 보통 (노랑)
  if (recipe.difficulty === '쉬움') {
    diffBg = 'rgba(255,255,255,0.1)'; diffColor = '#ffffff'; diffBorder = 'rgba(255,255,255,0.3)'; // 흰색
  } else if (recipe.difficulty === '어려움') {
    diffBg = 'rgba(255,99,71,0.15)'; diffColor = '#ff6347'; diffBorder = 'rgba(255,99,71,0.3)'; // 빨강
  }

  div.innerHTML = `
    ${imageHTML}
    <span style="position:absolute; top:1rem; right:1rem; font-size:0.72rem; background:${diffBg}; color:${diffColor}; border:1px solid ${diffBorder}; padding:0.2rem 0.6rem; border-radius:50px; font-weight:500; z-index:3;">⭐ ${recipe.difficulty}</span>
    ${recipe.image_url ? '' : `<span class="card-emoji">${recipe.emoji}</span>`}
    <div class="card-name">${recipe.name}</div>
    <div class="card-desc">${recipe.description}</div>
    <div class="card-tags">${tagHTML}</div>
  `;

  div.addEventListener('click', () => openModal(recipe, matchedKeywords));
  div.addEventListener('keydown', e => { if (e.key === 'Enter' || e.key === ' ') openModal(recipe, matchedKeywords); });
  return div;
}

// ===== MODAL =====
function openModal(recipe, matchedKeywords) {
  selectedModal = recipe;
  
  const modalHero = document.getElementById('modalHero');
  const modalNoHero = document.getElementById('modalNoHero');
  const modalImage = document.getElementById('modalImage');
  const modalEmoji = document.getElementById('modalEmoji');
  const modalEmojiDefault = document.getElementById('modalNoHero');

  if (recipe.image_url) {
    const displayUrl = normalizeImageUrl(recipe.image_url);
    modalHero.classList.remove('hidden');
    modalNoHero.classList.add('hidden');
    modalImage.src = displayUrl;
    modalEmoji.classList.add('hidden'); // Hide emoji when image exists
  } else {
    modalHero.classList.add('hidden');
    modalNoHero.classList.remove('hidden');
    modalNoHero.textContent = recipe.emoji;
  }

  document.getElementById('modalTitle').textContent = recipe.name;

  let diffBg = 'rgba(255,215,0,0.15)', diffColor = '#ffd700', diffBorder = 'rgba(255,215,0,0.3)'; // 보통
  if (recipe.difficulty === '쉬움') {
    diffBg = 'rgba(255,255,255,0.1)'; diffColor = '#ffffff'; diffBorder = 'rgba(255,255,255,0.3)'; // 쉬움
  } else if (recipe.difficulty === '어려움') {
    diffBg = 'rgba(255,99,71,0.15)'; diffColor = '#ff6347'; diffBorder = 'rgba(255,99,71,0.3)'; // 어려움
  }

  document.getElementById('modalBadges').innerHTML = `
    <span class="modal-badge" style="background:${diffBg}; color:${diffColor}; border:1px solid ${diffBorder};">⭐ ${recipe.difficulty}</span>
  `;

  document.getElementById('modalIngredients').innerHTML = recipe.ingredients.map(ing => {
    const isMatch = matchedKeywords.some(kw =>
      normalize(ing).includes(normalize(kw)) || normalize(kw).includes(normalize(ing))
    );
    return `<li class="${isMatch ? 'highlight' : ''}">${ing}</li>`;
  }).join('');

  document.getElementById('modalSteps').innerHTML = recipe.steps.map(s => `<li>${s}</li>`).join('');
  document.getElementById('modalTip').textContent = recipe.tip;

  // Reset to view mode
  recipeModal.classList.remove('hidden');
  document.body.style.overflow = 'hidden';
}

function openEditForm() {
  if (!selectedModal) return;
  
  editingRecipeId = selectedModal.id;
  
  // Fill the form
  document.getElementById('newName').value = selectedModal.name;
  document.getElementById('newEmoji').value = selectedModal.emoji;
  document.getElementById('newDifficulty').value = selectedModal.difficulty;
  document.getElementById('newIngredients').value = selectedModal.ingredients.join(', ');
  document.getElementById('newImageUrl').value = normalizeImageUrl(selectedModal.image_url);
  document.getElementById('newDescription').value = selectedModal.description;
  document.getElementById('newSteps').value = selectedModal.steps.join('\n');
  document.getElementById('newTip').value = selectedModal.tip;
  
  // Trigger preview
  if (selectedModal.image_url) {
    document.getElementById('imagePreview').classList.remove('hidden');
    document.getElementById('previewImg').src = normalizeImageUrl(selectedModal.image_url);
  } else {
    document.getElementById('imagePreview').classList.add('hidden');
  }

  // Change texts
  formModalTitle.textContent = '레시피 수정 ✏️';
  formModalSubtitle.textContent = '기존 메뉴의 내용을 수정합니다.';
  formSubmitBtn.textContent = '수정하기';

  // Close detail modal and open form modal
  closeModal();
  addRecipeModal.classList.remove('hidden');
  document.body.style.overflow = 'hidden';
}

async function deleteRecipe() {
  if (!selectedModal) return;

  const confirmed = confirm(`'${selectedModal.name}' 레시피를 정말로 삭제하시겠습니까?`);
  if (!confirmed) return;

  deleteBtn.textContent = '삭제 중...';
  deleteBtn.disabled = true;

  const deletedId = selectedModal.id;

  const { error } = await supabaseClient
    .from('recipes')
    .delete()
    .eq('id', deletedId);

  deleteBtn.textContent = '🗑️ 삭제';
  deleteBtn.disabled = false;

  if (error) {
    console.error('Error deleting recipe:', error);
    alert('삭제에 실패했습니다. 다시 시도해 주세요.');
    return;
  }

  // Remove from global array
  RECIPES = RECIPES.filter(r => r.id !== deletedId);

  // Close modal first
  closeModal();

  // Refresh UI
  const raw = searchInput.value.trim();
  if (raw) {
    // Active search — re-run to update results
    search();
  } else {
    // No search query — remove the deleted card directly from DOM
    const card = recipeGrid.querySelector(`[data-recipe-id="${deletedId}"]`);
    if (card) card.remove();

    // Update result count
    const countBadge = document.getElementById('resultsCount');
    if (countBadge) {
      const current = parseInt(countBadge.textContent) || 0;
      if (current > 0) countBadge.textContent = `${current - 1}개 레시피`;
    }

    // Show empty state if no cards left
    if (recipeGrid.children.length === 0) {
      resultsHeader.classList.add('hidden');
      emptyState.classList.remove('hidden');
    }
  }
}

function closeModal() {
  recipeModal.classList.add('hidden');
  document.body.style.overflow = '';
  selectedModal = null;
}

function openAddModal() {
  editingRecipeId = null;
  addRecipeForm.reset();
  document.getElementById('imagePreview').classList.add('hidden');
  formModalTitle.textContent = '새 레시피 등록 🍳';
  formModalSubtitle.textContent = '나만의 특별한 유아식 메뉴를 추가해보세요.';
  formSubmitBtn.textContent = '저장하기';
  
  addRecipeModal.classList.remove('hidden');
  document.body.style.overflow = 'hidden';
}

function closeAddModal() {
  addRecipeModal.classList.add('hidden');
  document.body.style.overflow = '';
}

async function handleAddRecipe(e) {
  e.preventDefault();

  const name = document.getElementById('newName').value.trim();
  const emoji = document.getElementById('newEmoji').value.trim() || '🍱';
  const difficulty = document.getElementById('newDifficulty').value;
  const ingredientsStr = document.getElementById('newIngredients').value.trim();
  const imageUrl = normalizeImageUrl(document.getElementById('newImageUrl').value);
  const description = document.getElementById('newDescription').value.trim() || '새로운 유아식 메뉴입니다.';
  const stepsStr = document.getElementById('newSteps').value.trim();
  const tip = document.getElementById('newTip').value.trim() || '아이의 기호에 맞게 조절해주세요.';

  if (!name || !ingredientsStr || !stepsStr) {
    alert('필수 항목을 모두 입력해주세요.');
    return;
  }

  const ingredients = ingredientsStr.split(/[,，\s]+/).map(s => s.trim()).filter(Boolean);
  const steps = stepsStr.split('\n').map(s => s.trim()).filter(Boolean);

  const recipeData = {
    emoji,
    name,
    difficulty,
    ingredients,
    image_url: imageUrl,
    description,
    steps,
    tip
  };

  const submitBtn = e.target.querySelector('button[type="submit"]');
  submitBtn.textContent = '저장 중...';
  submitBtn.disabled = true;

  if (editingRecipeId) {
    // === UPDATE EXISTING ===
    const { error } = await supabaseClient
      .from('recipes')
      .update(recipeData)
      .eq('id', editingRecipeId);

    submitBtn.textContent = '수정하기';
    submitBtn.disabled = false;

    if (error) {
      console.error('Error updating recipe:', error);
      alert('수정에 실패했습니다. 다시 시도해 주세요.');
      return;
    }

    // Update global array
    const idx = RECIPES.findIndex(r => r.id === editingRecipeId);
    if (idx !== -1) {
      RECIPES[idx] = { ...RECIPES[idx], ...recipeData };
    }
  } else {
    // === INSERT NEW ===
    recipeData.id = Date.now(); // Generate new ID
    const { error } = await supabaseClient
      .from('recipes')
      .insert([recipeData]);

    submitBtn.textContent = '저장하기';
    submitBtn.disabled = false;

    if (error) {
      console.error('Error adding new recipe:', error);
      alert('등록에 실패했습니다. 다시 시도해 주세요.');
      return;
    }

    // Add to global array
    RECIPES.unshift(recipeData);
  }

  // Visual Feedback & Refresh
  closeAddModal();

  // Search for the added/edited recipe to show it
  searchInput.value = name;
  search();

  // Scroll to results
  resultsSection.scrollIntoView({ behavior: 'smooth' });
}

// ===== EVENT LISTENERS =====
viewAllBtn.addEventListener('click', () => {
  searchInput.value = '';
  currentKeywords = [];
  document.querySelectorAll('#popularTags .tag').forEach(t => t.classList.remove('active'));
  
  // Show all recipes
  const results = RECIPES.map(recipe => ({ recipe, matched: [] }));
  renderResults(results, '전체 메뉴');
});

searchInput.addEventListener('keydown', e => {
  if (e.key === 'Enter') {
    if (searchTimeout) clearTimeout(searchTimeout);
    search();
  }
});

clearBtn.addEventListener('click', () => {
  searchInput.value = '';
  searchInput.focus();
  currentKeywords = [];
  recipeGrid.innerHTML = '';
  resultsHeader.classList.add('hidden');
  emptyState.classList.add('hidden');
  initialState.classList.remove('hidden');
  // Reset active tags
  document.querySelectorAll('.tag').forEach(t => t.classList.remove('active'));
});

modalClose.addEventListener('click', closeModal);

addRecipeBtn.addEventListener('click', openAddModal);
addModalClose.addEventListener('click', closeAddModal);
addModalCancel.addEventListener('click', closeAddModal);
addRecipeForm.addEventListener('submit', handleAddRecipe);

addRecipeModal.addEventListener('click', e => {
  if (e.target === addRecipeModal) closeAddModal();
});

editBtn.addEventListener('click', openEditForm);
deleteBtn.addEventListener('click', deleteRecipe);

recipeModal.addEventListener('click', e => {
  if (e.target === recipeModal) closeModal();
});
// Image Preview Listener
document.getElementById('newImageUrl').addEventListener('input', (e) => {
  const url = normalizeImageUrl(e.target.value);
  const preview = document.getElementById('imagePreview');
  const img = document.getElementById('previewImg');
  
  if (url) {
    img.src = url;
    preview.classList.remove('hidden');
    img.onerror = () => preview.classList.add('hidden');
  } else {
    preview.classList.add('hidden');
  }
});

// ===== POPULAR TAGS =====
function renderMainTags() {
  popularTagsContainer.innerHTML = '';
  popularTags.forEach(tag => {
    const btn = document.createElement('button');
    btn.className = 'tag';
    btn.dataset.value = tag.value;
    btn.textContent = tag.label;
    
    // Maintain active state if it was in the input
    if (currentKeywords.includes(normalize(tag.value))) {
      btn.classList.add('active');
    }

    btn.addEventListener('click', () => {
      const value = tag.value;
      const current = searchInput.value.trim();
      const normalizedValue = normalize(value);
      
      // Parse current keywords to check if already present
      let parts = current.split(/[,，\s]+/).map(k => k.trim()).filter(Boolean);
      const isAlreadyIncluded = parts.some(p => normalize(p) === normalizedValue);

      if (isAlreadyIncluded) {
        // Remove it
        parts = parts.filter(p => normalize(p) !== normalizedValue);
        searchInput.value = parts.join(', ');
      } else {
        // Add it
        if (current) {
          searchInput.value = `${current}, ${value}`;
        } else {
          searchInput.value = value;
        }
      }
      
      // Sync all tags' visual state and trigger search
      syncTagsWithInput();
      search();
    });
    
    popularTagsContainer.appendChild(btn);
  });
}

// Helper to sync tag buttons with search input
function syncTagsWithInput() {
  const raw = searchInput.value.trim();
  const keywords = raw.split(/[,，\s]+/).map(k => normalize(k)).filter(Boolean);
  
  const tagButtons = popularTagsContainer.querySelectorAll('.tag');
  tagButtons.forEach(btn => {
    const val = normalize(btn.dataset.value);
    if (keywords.includes(val)) {
      btn.classList.add('active');
    } else {
      btn.classList.remove('active');
    }
  });
}

// Initial render
renderMainTags();

// Add input listener for real-time tag syncing and live search while typing
searchInput.addEventListener('input', () => {
  syncTagsWithInput();
  handleLiveSearch();
});

// Edit Tags Logic
function openEditTagsModal() {
  tempEditTags = [...popularTags];
  renderEditTags();
  newTagInput.value = '';
  editTagsModal.classList.remove('hidden');
  document.body.style.overflow = 'hidden';
}

function closeEditTagsModal() {
  editTagsModal.classList.add('hidden');
  document.body.style.overflow = '';
}

function renderEditTags() {
  editTagsList.innerHTML = '';
  tempEditTags.forEach((tag, idx) => {
    const btn = document.createElement('button');
    btn.className = 'tag';
    btn.title = '클릭하여 삭제';
    btn.innerHTML = `${tag.label} <span style="margin-left:6px; color:#fca5a5; font-size:0.75rem;">✕</span>`;
    btn.style.borderColor = 'rgba(252,165,165,0.3)';
    btn.style.background = 'rgba(255,255,255,0.04)';
    
    btn.addEventListener('click', () => {
      tempEditTags.splice(idx, 1);
      renderEditTags();
    });
    
    editTagsList.appendChild(btn);
  });
}

addTagBtn.addEventListener('click', () => {
  const val = newTagInput.value.trim();
  if (val) {
    // Basic label matching (just the value if no emoji included)
    tempEditTags.push({ value: val, label: val });
    newTagInput.value = '';
    renderEditTags();
  }
});

newTagInput.addEventListener('keydown', e => {
  if (e.key === 'Enter') {
    e.preventDefault();
    addTagBtn.click();
  }
});

saveTagsBtn.addEventListener('click', () => {
  popularTags = [...tempEditTags];
  localStorage.setItem('popularTags', JSON.stringify(popularTags));
  renderMainTags();
  closeEditTagsModal();
});

editTagsBtn.addEventListener('click', openEditTagsModal);
editTagsClose.addEventListener('click', closeEditTagsModal);
editTagsCancel.addEventListener('click', closeEditTagsModal);
editTagsModal.addEventListener('click', e => {
  if (e.target === editTagsModal) closeEditTagsModal();
});
