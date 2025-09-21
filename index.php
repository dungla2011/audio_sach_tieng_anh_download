<?php
/**
 * Audio Player - Main PHP file
 * 
 * Serves the audio player interface and handles file serving
 */

// Configuration
$downloadDir = __DIR__ . '/Download';

// Handle file serving requests
if (isset($_GET['play']) && !empty($_GET['play'])) {
    $filePath = $_GET['play'];
    $fullPath = $downloadDir . DIRECTORY_SEPARATOR . $filePath;
    
    // Security check - prevent directory traversal
    $realPath = realpath($fullPath);
    $realDownloadDir = realpath($downloadDir);
    
    if (!$realPath || strpos($realPath, $realDownloadDir) !== 0) {
        http_response_code(403);
        die('Access denied');
    }
    
    if (!file_exists($realPath) || !is_file($realPath)) {
        http_response_code(404);
        die('File not found');
    }
    
    // Get file info
    $info = pathinfo($realPath);
    $extension = strtolower($info['extension']);
    
    // Set appropriate headers for audio streaming
    $mimeTypes = [
        'mp3' => 'audio/mpeg',
        'wav' => 'audio/wav',
        'm4a' => 'audio/mp4',
        'flac' => 'audio/flac',
        'ogg' => 'audio/ogg',
        'aac' => 'audio/aac'
    ];
    
    $mimeType = isset($mimeTypes[$extension]) ? $mimeTypes[$extension] : 'audio/mpeg';
    
    // Handle range requests for better audio streaming
    $fileSize = filesize($realPath);
    $start = 0;
    $end = $fileSize - 1;
    
    if (isset($_SERVER['HTTP_RANGE'])) {
        $range = $_SERVER['HTTP_RANGE'];
        list($param, $range) = explode('=', $range);
        
        if (strtolower(trim($param)) === 'bytes') {
            $range = explode(',', $range);
            $range = explode('-', $range[0]);
            
            if (count($range) == 2) {
                if (is_numeric($range[0])) {
                    $start = intval($range[0]);
                }
                if (is_numeric($range[1])) {
                    $end = intval($range[1]);
                }
            }
        }
        
        header('HTTP/1.1 206 Partial Content');
        header("Content-Range: bytes $start-$end/$fileSize");
    } else {
        header('HTTP/1.1 200 OK');
    }
    
    header("Content-Type: $mimeType");
    header("Content-Length: " . ($end - $start + 1));
    header("Accept-Ranges: bytes");
    header("Cache-Control: public, max-age=3600");
    header("Content-Disposition: inline; filename=\"" . basename($realPath) . "\"");
    
    // Stream the file
    $handle = fopen($realPath, 'rb');
    fseek($handle, $start);
    
    $chunkSize = 8192;
    $bytesRemaining = $end - $start + 1;
    
    while ($bytesRemaining > 0 && !feof($handle)) {
        $bytesToRead = min($chunkSize, $bytesRemaining);
        echo fread($handle, $bytesToRead);
        $bytesRemaining -= $bytesToRead;
        
        if (ob_get_level()) {
            ob_flush();
        }
        flush();
    }
    
    fclose($handle);
    exit;
}

// Serve the HTML interface
include 'audio_player.html';
?>