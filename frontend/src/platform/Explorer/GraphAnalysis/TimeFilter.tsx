/**
 * TimeFilter - Temporal Filter Panel
 * MDP Platform V3.1 - Graph Analysis Module
 *
 * Features:
 * - Time range slider for filtering edges by valid_start/valid_end
 * - Play/pause animation to scrub through time
 */

import React, { useState, useCallback, useMemo } from "react";
import { Slider, Space, Button, Typography, DatePicker, Tooltip } from "antd";
import {
  PlayCircleOutlined,
  PauseCircleOutlined,
  ClockCircleOutlined,
  HistoryOutlined,
} from "@ant-design/icons";
import dayjs, { Dayjs } from "dayjs";

const { Text } = Typography;
const { RangePicker } = DatePicker;

interface TimeFilterProps {
  minTime?: Date;
  maxTime?: Date;
  value: [Date, Date] | null;
  onChange: (range: [Date, Date] | null) => void;
}

const TimeFilter: React.FC<TimeFilterProps> = ({
  minTime = new Date(Date.now() - 24 * 60 * 60 * 1000), // 24 hours ago
  maxTime = new Date(),
  value,
  onChange,
}) => {
  const [isPlaying, setIsPlaying] = useState(false);

  // Convert to dayjs for slider
  const minTimestamp = minTime.getTime();
  const maxTimestamp = maxTime.getTime();

  // Current slider value (as [start, end] timestamps)
  const sliderValue = useMemo<[number, number]>(() => {
    if (value) {
      return [value[0].getTime(), value[1].getTime()];
    }
    return [minTimestamp, maxTimestamp];
  }, [value, minTimestamp, maxTimestamp]);

  // Handle slider change
  const handleSliderChange = useCallback(
    (newValue: number | number[]) => {
      if (Array.isArray(newValue) && newValue.length === 2) {
        onChange([new Date(newValue[0]), new Date(newValue[1])]);
      }
    },
    [onChange]
  );

  // Handle date picker change
  const handleRangePickerChange = useCallback(
    (dates: [Dayjs | null, Dayjs | null] | null) => {
      if (dates && dates[0] && dates[1]) {
        onChange([dates[0].toDate(), dates[1].toDate()]);
      } else {
        onChange(null);
      }
    },
    [onChange]
  );

  // Format timestamp for display
  const formatTime = (timestamp: number) => {
    return dayjs(timestamp).format("MM-DD HH:mm");
  };

  // Reset to full range
  const handleReset = () => {
    onChange(null);
  };

  // Toggle play/pause (future: animate through time)
  const handlePlayPause = () => {
    setIsPlaying(!isPlaying);
    // TODO: Implement time scrubbing animation
  };

  return (
    <div
      style={{
        background: "#1f1f1f",
        borderTop: "1px solid #333",
        padding: "12px 24px",
      }}
    >
      <Space direction="vertical" style={{ width: "100%" }} size="small">
        {/* Header */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
          }}
        >
          <Space>
            <ClockCircleOutlined style={{ color: "#1890ff" }} />
            <Text style={{ color: "#aaa" }}>时间过滤器</Text>
          </Space>

          <Space>
            <Tooltip title="重置">
              <Button
                type="text"
                size="small"
                icon={<HistoryOutlined />}
                onClick={handleReset}
                style={{ color: "#666" }}
              />
            </Tooltip>
            <Tooltip title={isPlaying ? "暂停" : "播放时间线"}>
              <Button
                type="text"
                size="small"
                icon={isPlaying ? <PauseCircleOutlined /> : <PlayCircleOutlined />}
                onClick={handlePlayPause}
                style={{ color: "#666" }}
              />
            </Tooltip>
          </Space>
        </div>

        {/* Time Slider */}
        <div style={{ padding: "0 8px" }}>
          <Slider
            range
            min={minTimestamp}
            max={maxTimestamp}
            value={sliderValue}
            onChange={handleSliderChange}
            tooltip={{
              formatter: (val) => (val ? formatTime(val) : ""),
            }}
            styles={{
              track: { background: "#1890ff" },
              rail: { background: "#333" },
            }}
          />
        </div>

        {/* Date Picker & Current Range */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
          }}
        >
          <RangePicker
            showTime
            size="small"
            value={
              value
                ? [dayjs(value[0]), dayjs(value[1])]
                : [dayjs(minTime), dayjs(maxTime)]
            }
            onChange={handleRangePickerChange}
            format="MM-DD HH:mm"
            style={{ background: "#141414" }}
          />

          <Text style={{ color: "#666", fontSize: 12 }}>
            当前范围: {formatTime(sliderValue[0])} ~ {formatTime(sliderValue[1])}
          </Text>
        </div>
      </Space>
    </div>
  );
};

export default TimeFilter;
