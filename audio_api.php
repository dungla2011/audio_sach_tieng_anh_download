<?php
/**
 * Audio API - Scan and return audio files from Download directory
 * 
 * Returns JSON with folder structure and audio files
 */

header('Content-Type: application/json; charset=utf-8');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');

// Configuration
$downloadDir = 'g:/Download_TiengAnhAudio';
$allowedExtensions = ['mp3', 'wav', 'm4a', 'flac', 'ogg', 'aac'];
$maxDepth = 3; // Maximum directory depth to scan

class AudioScanner {
    private $downloadDir;
    private $allowedExtensions;
    private $maxDepth;
    private $baseUrl;
    
    public function __construct($downloadDir, $allowedExtensions, $maxDepth) {
        $this->downloadDir = $downloadDir;
        $this->allowedExtensions = $allowedExtensions;
        $this->maxDepth = $maxDepth;
        $this->baseUrl = $this->getBaseUrl();
    }
    
    private function getBaseUrl() {
        $protocol = isset($_SERVER['HTTPS']) && $_SERVER['HTTPS'] === 'on' ? 'https' : 'http';
        $host = $_SERVER['HTTP_HOST'];
        $path = dirname($_SERVER['REQUEST_URI']);
        return $protocol . '://' . $host . $path;
    }
    
    public function scanAudioFiles() {
        try {
            if (!is_dir($this->downloadDir)) {
                throw new Exception("Download directory not found: " . $this->downloadDir);
            }
            
            $folders = [];
            $stats = [
                'totalFolders' => 0,
                'totalFiles' => 0,
                'totalSize' => 0
            ];
            
            $this->scanDirectory($this->downloadDir, $folders, $stats, 0);
            
            // Sort folders by name
            usort($folders, function($a, $b) {
                return strcasecmp($a['name'], $b['name']);
            });
            
            return [
                'success' => true,
                'folders' => $folders,
                'stats' => $stats,
                'scannedAt' => date('Y-m-d H:i:s'),
                'baseDir' => $this->downloadDir
            ];
            
        } catch (Exception $e) {
            return [
                'success' => false,
                'message' => $e->getMessage(),
                'error' => true
            ];
        }
    }
    
    private function scanDirectory($dir, &$folders, &$stats, $depth) {
        if ($depth > $this->maxDepth) {
            return;
        }
        
        $items = [];
        
        try {
            $iterator = new DirectoryIterator($dir);
            
            foreach ($iterator as $item) {
                if ($item->isDot()) continue;
                
                $fullPath = $item->getPathname();
                $relativePath = str_replace($this->downloadDir . DIRECTORY_SEPARATOR, '', $fullPath);
                
                if ($item->isDir()) {
                    // Recursively scan subdirectories
                    $this->scanDirectory($fullPath, $folders, $stats, $depth + 1);
                } elseif ($item->isFile()) {
                    $extension = strtolower($item->getExtension());
                    
                    if (in_array($extension, $this->allowedExtensions)) {
                        $audioFile = [
                            'name' => $item->getFilename(),
                            'size' => $item->getSize(),
                            'extension' => $extension,
                            'modified' => date('Y-m-d H:i:s', $item->getMTime()),
                            'url' => $this->baseUrl . '/Download/' . str_replace('\\', '/', $relativePath),
                            'path' => $relativePath
                        ];
                        
                        $items[] = $audioFile;
                        $stats['totalFiles']++;
                        $stats['totalSize'] += $item->getSize();
                    }
                }
            }
            
        } catch (Exception $e) {
            error_log("Error scanning directory $dir: " . $e->getMessage());
            return;
        }
        
        // If this directory has audio files, add it to folders
        if (!empty($items)) {
            $folderName = basename($dir);
            
            // Sort files by name
            usort($items, function($a, $b) {
                return strnatcasecmp($a['name'], $b['name']);
            });
            
            $folders[] = [
                'name' => $folderName,
                'path' => str_replace($this->downloadDir . DIRECTORY_SEPARATOR, '', $dir),
                'files' => $items,
                'fileCount' => count($items),
                'totalSize' => array_sum(array_column($items, 'size'))
            ];
            
            $stats['totalFolders']++;
        }
    }
    
    public function getAudioFileInfo($filePath) {
        $fullPath = $this->downloadDir . DIRECTORY_SEPARATOR . $filePath;
        
        if (!file_exists($fullPath) || !is_file($fullPath)) {
            throw new Exception("File not found: $filePath");
        }
        
        $info = pathinfo($fullPath);
        $extension = strtolower($info['extension']);
        
        if (!in_array($extension, $this->allowedExtensions)) {
            throw new Exception("File type not allowed: $extension");
        }
        
        return [
            'name' => $info['basename'],
            'size' => filesize($fullPath),
            'extension' => $extension,
            'modified' => date('Y-m-d H:i:s', filemtime($fullPath)),
            'url' => $this->baseUrl . '/Download/' . str_replace('\\', '/', $filePath)
        ];
    }
}

// Handle different request types
$requestMethod = $_SERVER['REQUEST_METHOD'];
$requestUri = $_SERVER['REQUEST_URI'];

try {
    $scanner = new AudioScanner($downloadDir, $allowedExtensions, $maxDepth);
    
    if ($requestMethod === 'GET') {
        // Check if requesting specific file info
        if (isset($_GET['file'])) {
            $filePath = $_GET['file'];
            $result = $scanner->getAudioFileInfo($filePath);
        } else {
            // Return full directory scan
            $result = $scanner->scanAudioFiles();
        }
        
        echo json_encode($result, JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT);
        
    } else {
        throw new Exception("Method not allowed: $requestMethod");
    }
    
} catch (Exception $e) {
    http_response_code(500);
    echo json_encode([
        'success' => false,
        'message' => $e->getMessage(),
        'error' => true
    ], JSON_UNESCAPED_UNICODE);
}

/**
 * Helper function to format file size
 */
function formatBytes($size, $precision = 2) {
    $base = log($size, 1024);
    $suffixes = ['B', 'KB', 'MB', 'GB', 'TB'];
    return round(pow(1024, $base - floor($base)), $precision) . ' ' . $suffixes[floor($base)];
}

/**
 * Helper function to get MIME type for audio files
 */
function getAudioMimeType($extension) {
    $mimeTypes = [
        'mp3' => 'audio/mpeg',
        'wav' => 'audio/wav',
        'm4a' => 'audio/mp4',
        'flac' => 'audio/flac',
        'ogg' => 'audio/ogg',
        'aac' => 'audio/aac'
    ];
    
    return isset($mimeTypes[$extension]) ? $mimeTypes[$extension] : 'audio/mpeg';
}
?>