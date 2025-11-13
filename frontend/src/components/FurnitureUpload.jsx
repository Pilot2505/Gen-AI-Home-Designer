import { useState } from "react";
import { Upload, Input, Select, Button, Card, message, Spin } from "antd";
import { InboxOutlined, DeleteOutlined } from "@ant-design/icons";
import axios from "axios";

const { Dragger } = Upload;
const { Option } = Select;

const FurnitureUpload = ({ isDarkMode, onFurnitureUploaded }) => {
  const [uploading, setUploading] = useState(false);
  const [furnitureImage, setFurnitureImage] = useState(null);
  const [furnitureName, setFurnitureName] = useState("");
  const [furnitureCategory, setFurnitureCategory] = useState("");
  const [preview, setPreview] = useState(null);

  const uploadProps = {
    name: "file",
    multiple: false,
    maxCount: 1,
    accept: "image/*",
    showUploadList: false,
    beforeUpload: (file) => {
      const isImage = file.type.startsWith("image/");
      if (!isImage) {
        message.error("You can only upload image files!");
        return Upload.LIST_IGNORE;
      }

      const isLt10M = file.size / 1024 / 1024 < 10;
      if (!isLt10M) {
        message.error("Image must be smaller than 10MB!");
        return Upload.LIST_IGNORE;
      }

      const reader = new FileReader();
      reader.onloadend = () => {
        setPreview(reader.result);
        setFurnitureImage(file);
      };
      reader.readAsDataURL(file);
      return false;
    },
  };

  const handleUpload = async () => {
    if (!furnitureImage) {
      message.error("Please select a furniture image");
      return;
    }
    if (!furnitureName) {
      message.error("Please enter furniture name");
      return;
    }
    if (!furnitureCategory) {
      message.error("Please select furniture category");
      return;
    }

    setUploading(true);

    const formData = new FormData();
    formData.append("furniture_image", furnitureImage);
    formData.append("name", furnitureName);
    formData.append("category", furnitureCategory);

    try {
      const response = await axios.post(
        "http://127.0.0.1:8000/api/furniture/upload",
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        }
      );

      message.success("Furniture uploaded successfully!");

      if (onFurnitureUploaded) {
        onFurnitureUploaded(response.data);
      }

      setPreview(null);
      setFurnitureImage(null);
      setFurnitureName("");
      setFurnitureCategory("");
    } catch (error) {
      message.error("Failed to upload furniture");
      console.error(error);
    } finally {
      setUploading(false);
    }
  };

  const handleRemove = () => {
    setPreview(null);
    setFurnitureImage(null);
  };

  return (
    <Card
      title="Upload Your Furniture"
      style={{
        background: isDarkMode ? "#1f1f1f" : "#ffffff",
        borderRadius: 12,
        marginBottom: 24,
      }}
    >
      <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
        {preview ? (
          <div style={{ position: "relative", textAlign: "center" }}>
            <img
              src={preview}
              alt="Furniture Preview"
              style={{
                maxWidth: "100%",
                maxHeight: "240px",
                objectFit: "contain",
                borderRadius: 8,
              }}
            />
            <DeleteOutlined
              onClick={handleRemove}
              style={{
                position: "absolute",
                top: -10,
                right: -10,
                fontSize: 20,
                color: "#ef4444",
                backgroundColor: isDarkMode ? "#1f1f1f" : "#ffffff",
                borderRadius: "50%",
                padding: 4,
                cursor: "pointer",
                boxShadow: "0 2px 6px rgba(0,0,0,0.2)",
              }}
            />
          </div>
        ) : (
          <Dragger
            {...uploadProps}
            style={{
              border: `1px dashed ${isDarkMode ? "#444" : "#d9d9d9"}`,
              borderRadius: 8,
              backgroundColor: isDarkMode ? "#1f1f1f" : "#fafafa",
            }}
          >
            <p className="ant-upload-drag-icon">
              <InboxOutlined
                style={{ color: isDarkMode ? "#38bdf8" : "#1677ff" }}
              />
            </p>
            <p
              className="ant-upload-text"
              style={{ color: isDarkMode ? "#e5e5e5" : "#333" }}
            >
              Click or drag furniture image here
            </p>
          </Dragger>
        )}

        <Input
          placeholder="Furniture name (e.g., Modern Sofa)"
          value={furnitureName}
          onChange={(e) => setFurnitureName(e.target.value)}
          style={{ width: "100%" }}
        />

        <Select
          placeholder="Select category"
          value={furnitureCategory}
          onChange={setFurnitureCategory}
          style={{ width: "100%" }}
        >
          <Option value="sofa">Sofa</Option>
          <Option value="chair">Chair</Option>
          <Option value="table">Table</Option>
          <Option value="lamp">Lamp</Option>
          <Option value="bed">Bed</Option>
          <Option value="cabinet">Cabinet</Option>
          <Option value="painting">Painting</Option>
          <Option value="plant">Plant</Option>
          <Option value="rug">Rug</Option>
          <Option value="other">Other</Option>
        </Select>

        <Button
          type="primary"
          onClick={handleUpload}
          loading={uploading}
          disabled={!furnitureImage || !furnitureName || !furnitureCategory}
          block
        >
          {uploading ? "Uploading..." : "Upload Furniture"}
        </Button>
      </div>
    </Card>
  );
};

export default FurnitureUpload;
