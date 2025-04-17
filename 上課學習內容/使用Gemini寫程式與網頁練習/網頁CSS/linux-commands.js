const commandDatabase = {
    'ls': {
        name: 'ls (List)',
        description: '列出目前目錄下的檔案與子目錄',
        example: 'ls -la\n# 顯示詳細檔案資訊，包含隱藏檔'
    },
    'cd': {
        name: 'cd (Change Directory)',
        description: '切換目前工作目錄',
        example: 'cd /home/user\n# 切換到指定目錄'
    },
    'mkdir': {
        name: 'mkdir (Make Directory)',
        description: '建立新目錄',
        example: 'mkdir -p test/subdir\n# 建立巢狀目錄'
    },
    'rm': {
        name: 'rm (Remove)',
        description: '刪除檔案或目錄',
        example: 'rm -rf directory\n# 遞迴刪除目錄及其內容'
    }
};

let searchHistory = [];

document.getElementById('searchBtn').addEventListener('click', searchCommand);
document.getElementById('searchInput').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        searchCommand();
    }
});

function searchCommand() {
    const input = document.getElementById('searchInput').value.toLowerCase();
    const resultCard = document.getElementById('commandResult');
    
    if (commandDatabase[input]) {
        const command = commandDatabase[input];
        resultCard.querySelector('.command-name').textContent = command.name;
        resultCard.querySelector('.command-desc').textContent = command.description;
        resultCard.querySelector('code').textContent = command.example;
        resultCard.classList.remove('hidden');
        
        // 加入搜尋歷史
        if (!searchHistory.includes(input)) {
            searchHistory.push(input);
            updateSearchHistory();
        }
    } else {
        alert('找不到該指令，請重新輸入！');
    }
}

function updateSearchHistory() {
    const historyContainer = document.getElementById('searchHistory');
    historyContainer.innerHTML = '';
    
    searchHistory.forEach(cmd => {
        const historyItem = document.createElement('span');
        historyItem.className = 'history-item';
        historyItem.textContent = cmd;
        historyItem.onclick = () => {
            document.getElementById('searchInput').value = cmd;
            searchCommand();
        };
        historyContainer.appendChild(historyItem);
    });
}

// 初始化搜尋歷史
updateSearchHistory();
