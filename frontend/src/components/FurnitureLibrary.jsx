import { useState, useEffect } from "react";
import { Card, Checkbox, Empty, Spin, message, Typography, Row, Col } from "antd";
import axios from "axios";

const { Text } = Typography;

const FurnitureLibrary = ({ isDarkMode, selectedFurniture, onSelectionChange }) => {
  const [furniture, setFurniture] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadFurniture();
  }, []);

  const loadFurniture = async () => {
    setLoading(true);
    try {
      const response = await axios.get("http://127.0.0.1:8000/api/furniture/list");
      setFurniture(response.data.furniture);
    } catch (error) {
      message.error("Failed to load furniture");
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const handleCheckboxChange = (furnitureId, checked) => {
    if (checked) {
      onSelectionChange([...selectedFurniture, furnitureId]);
    } else {
      onSelectionChange(selectedFurniture.filter((id) => id !== furnitureId));
    }
  };

  if (loading) {
    return (
      <Card
        title="Your Furniture Library"
        style={{
          background: isDarkMode ? "#1f1f1f" : "#ffffff",
          borderRadius: 12,
          marginBottom: 24,
        }}
      >
        <div style={{ textAlign: "center", padding: "2rem" }}>
          <Spin size="large" />
        </div>
      </Card>
    );
  }

  return (
    <Card
      title="Your Furniture Library"
      extra={
        <Text style={{ fontSize: 12, color: isDarkMode ? "#a1a1aa" : "#666" }}>
          Select items to include in your design
        </Text>
      }
      style={{
        background: isDarkMode ? "#1f1f1f" : "#ffffff",
        borderRadius: 12,
        marginBottom: 24,
      }}
    >
      {furniture.length === 0 ? (
        <Empty
          description="No furniture uploaded yet"
          style={{ padding: "2rem 0" }}
        />
      ) : (
        <Row gutter={[16, 16]}>
          {furniture.map((item) => (
            <Col xs={12} sm={8} md={6} key={item.id}>
              <div
                style={{
                  position: "relative",
                  border: selectedFurniture.includes(item.id)
                    ? "2px solid #0ea5e9"
                    : `1px solid ${isDarkMode ? "#333" : "#d9d9d9"}`,
                  borderRadius: 8,
                  padding: 8,
                  cursor: "pointer",
                  transition: "all 0.3s",
                  background: isDarkMode ? "#2a2a2a" : "#fafafa",
                }}
                onClick={() =>
                  handleCheckboxChange(
                    item.id,
                    !selectedFurniture.includes(item.id)
                  )
                }
              >
                <Checkbox
                  checked={selectedFurniture.includes(item.id)}
                  onChange={(e) =>
                    handleCheckboxChange(item.id, e.target.checked)
                  }
                  style={{
                    position: "absolute",
                    top: 8,
                    right: 8,
                    zIndex: 10,
                  }}
                  onClick={(e) => e.stopPropagation()}
                />
                <img
                  src={item.image_url}
                  alt={item.name}
                  style={{
                    width: "100%",
                    height: "120px",
                    objectFit: "cover",
                    borderRadius: 6,
                    marginBottom: 8,
                  }}
                />
                <Text
                  style={{
                    display: "block",
                    fontSize: 12,
                    fontWeight: 500,
                    color: isDarkMode ? "#e5e5e5" : "#333",
                    marginBottom: 4,
                    textOverflow: "ellipsis",
                    overflow: "hidden",
                    whiteSpace: "nowrap",
                  }}
                >
                  {item.name}
                </Text>
                <Text
                  style={{
                    display: "block",
                    fontSize: 11,
                    color: isDarkMode ? "#a1a1aa" : "#666",
                    textTransform: "capitalize",
                  }}
                >
                  {item.category}
                </Text>
              </div>
            </Col>
          ))}
        </Row>
      )}
    </Card>
  );
};

export default FurnitureLibrary;
