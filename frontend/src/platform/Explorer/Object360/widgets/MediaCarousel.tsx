/**
 * MediaCarousel Widget - Display Media Gallery
 * MDP Platform V3.1 - Object 360 View
 */

import React, { useState } from "react";
import {
  Card,
  Carousel,
  Image,
  Space,
  Typography,
  Empty,
  Button,
  Modal,
  Row,
  Col,
} from "antd";
import {
  PictureOutlined,
  LeftOutlined,
  RightOutlined,
  ExpandOutlined,
  PlayCircleOutlined,
  FileImageOutlined,
  VideoCameraOutlined,
} from "@ant-design/icons";
import type { WidgetProps } from "../types";

const { Text } = Typography;

const MediaCarousel: React.FC<WidgetProps> = ({ config, data }) => {
  const viewConfig = config.view_config || {};
  const dataBinding = config.data_binding || {};
  
  const title = viewConfig.title || "侦察影像";
  const autoPlay = viewConfig.autoPlay || false;
  const showThumbnails = viewConfig.showThumbnails !== false;
  
  const [currentIndex, setCurrentIndex] = useState(0);
  const [previewVisible, setPreviewVisible] = useState(false);
  const [previewImage, setPreviewImage] = useState("");

  // Get media URLs from data (with null check)
  const mediaUrls = data?.media_urls || [];
  
  // Mock some placeholder images if none exist
  const displayMedia = mediaUrls.length > 0
    ? mediaUrls
    : [
        // Placeholder images for demo
        "https://via.placeholder.com/400x300/1a1a2e/1890ff?text=No+Media+1",
        "https://via.placeholder.com/400x300/16213e/1890ff?text=No+Media+2",
        "https://via.placeholder.com/400x300/1f1f1f/1890ff?text=No+Media+3",
      ];

  // Check if URL is video
  const isVideo = (url: string) => {
    return /\.(mp4|webm|ogg|mov)$/i.test(url);
  };

  // Handle preview
  const handlePreview = (url: string) => {
    setPreviewImage(url);
    setPreviewVisible(true);
  };

  // Handle carousel change
  const handleCarouselChange = (current: number) => {
    setCurrentIndex(current);
  };

  // Carousel settings
  const carouselSettings = {
    autoplay: autoPlay,
    dots: false,
    afterChange: handleCarouselChange,
  };

  return (
    <Card
      size="small"
      title={
        <Space>
          <PictureOutlined />
          <span>{title}</span>
          {displayMedia.length > 0 && (
            <Text type="secondary" style={{ fontSize: 12 }}>
              ({currentIndex + 1}/{displayMedia.length})
            </Text>
          )}
        </Space>
      }
      extra={
        displayMedia.length > 0 && (
          <Button
            type="text"
            size="small"
            icon={<ExpandOutlined />}
            onClick={() => handlePreview(displayMedia[currentIndex])}
          />
        )
      }
      style={{ marginBottom: 16 }}
      styles={{
        body: { padding: 0 },
      }}
    >
      {displayMedia.length > 0 ? (
        <>
          {/* Main Carousel */}
          <div style={{ position: "relative" }}>
            <Carousel {...carouselSettings}>
              {displayMedia.map((url, index) => (
                <div key={index}>
                  <div
                    style={{
                      height: viewConfig.height || 200,
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      background: "#141414",
                      cursor: "pointer",
                    }}
                    onClick={() => handlePreview(url)}
                  >
                    {isVideo(url) ? (
                      <div
                        style={{
                          position: "relative",
                          width: "100%",
                          height: "100%",
                          display: "flex",
                          alignItems: "center",
                          justifyContent: "center",
                          background: "#000",
                        }}
                      >
                        <video
                          src={url}
                          style={{
                            maxWidth: "100%",
                            maxHeight: "100%",
                          }}
                        />
                        <PlayCircleOutlined
                          style={{
                            position: "absolute",
                            fontSize: 48,
                            color: "rgba(255,255,255,0.8)",
                          }}
                        />
                      </div>
                    ) : (
                      <Image
                        src={url}
                        alt={`Media ${index + 1}`}
                        style={{
                          maxHeight: viewConfig.height || 200,
                          objectFit: "contain",
                        }}
                        preview={false}
                        fallback="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAMIAAADDCAYAAADQvc6UAAABRWlDQ1BJQ0MgUHJvZmlsZQAAKJFjYGASSSwoyGFhYGDIzSspCnJ3UoiIjFJgf8LAwSDCIMogwMCcmFxc4BgQ4ANUwgCjUcG3awyMIPqyLsis7PPOq3QdDFcvjV3jOD1boQVTPQrgSkktTgbSf4A4LbmgqISBgTEFyFYuLykAsTuAbJEioKOA7DkgdjqEvQHEToKwj4DVhAQ5A9k3gGyB5IxEoBmML4BsnSQk8XQkNtReEOBxcfXxUQg1Mjc0dyHgXNJBSWpFCYh2zi+oLMpMzyhRcASGUqqCZ16yno6CkYGRAQMDKMwhqj/fAIcloxgHQqxAjIHBEugw5sUIsSQpBobtQPdLciLEVJYzMPBHMDBsayhILEqEO4DxG0txmrERhM29nYGBddr//5/DGRjYNRkY/l7////39v///y4Dmn+LgesASSQJsAIALqk="
                      />
                    )}
                  </div>
                </div>
              ))}
            </Carousel>
            
            {/* Navigation arrows */}
            {displayMedia.length > 1 && (
              <>
                <Button
                  type="text"
                  icon={<LeftOutlined />}
                  style={{
                    position: "absolute",
                    left: 8,
                    top: "50%",
                    transform: "translateY(-50%)",
                    background: "rgba(0,0,0,0.5)",
                    color: "#fff",
                    border: "none",
                  }}
                  onClick={() => {
                    const prev = currentIndex === 0 ? displayMedia.length - 1 : currentIndex - 1;
                    setCurrentIndex(prev);
                  }}
                />
                <Button
                  type="text"
                  icon={<RightOutlined />}
                  style={{
                    position: "absolute",
                    right: 8,
                    top: "50%",
                    transform: "translateY(-50%)",
                    background: "rgba(0,0,0,0.5)",
                    color: "#fff",
                    border: "none",
                  }}
                  onClick={() => {
                    const next = currentIndex === displayMedia.length - 1 ? 0 : currentIndex + 1;
                    setCurrentIndex(next);
                  }}
                />
              </>
            )}
          </div>

          {/* Thumbnails */}
          {showThumbnails && displayMedia.length > 1 && (
            <div
              style={{
                padding: "8px 12px",
                borderTop: "1px solid #303030",
                display: "flex",
                gap: 8,
                overflowX: "auto",
              }}
            >
              {displayMedia.map((url, index) => (
                <div
                  key={index}
                  onClick={() => setCurrentIndex(index)}
                  style={{
                    width: 48,
                    height: 36,
                    borderRadius: 4,
                    overflow: "hidden",
                    cursor: "pointer",
                    border: index === currentIndex ? "2px solid #1890ff" : "2px solid transparent",
                    flexShrink: 0,
                  }}
                >
                  {isVideo(url) ? (
                    <div
                      style={{
                        width: "100%",
                        height: "100%",
                        background: "#000",
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                      }}
                    >
                      <VideoCameraOutlined style={{ color: "#666" }} />
                    </div>
                  ) : (
                    <img
                      src={url}
                      alt={`Thumb ${index + 1}`}
                      style={{
                        width: "100%",
                        height: "100%",
                        objectFit: "cover",
                      }}
                    />
                  )}
                </div>
              ))}
            </div>
          )}
        </>
      ) : (
        <div style={{ padding: 24 }}>
          <Empty
            image={<FileImageOutlined style={{ fontSize: 48, color: "#666" }} />}
            description="暂无媒体文件"
          />
        </div>
      )}

      {/* Preview Modal */}
      <Modal
        open={previewVisible}
        title={null}
        footer={null}
        onCancel={() => setPreviewVisible(false)}
        width="80%"
        centered
        styles={{
          body: { padding: 0, background: "#000" },
        }}
      >
        {isVideo(previewImage) ? (
          <video
            src={previewImage}
            controls
            autoPlay
            style={{ width: "100%", maxHeight: "80vh" }}
          />
        ) : (
          <Image
            src={previewImage}
            alt="Preview"
            style={{ width: "100%" }}
            preview={false}
          />
        )}
      </Modal>
    </Card>
  );
};

export default MediaCarousel;
