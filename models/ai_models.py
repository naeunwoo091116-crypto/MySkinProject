"""
AI 모델 클래스 정의
"""
import torch
import torch.nn as nn
from torchvision import models


class ResNetBalanced(nn.Module):
    """
    분류 + 회귀 이중 헤드 ResNet 모델

    Args:
        num_classes: 분류 클래스 수
        num_regression_targets: 회귀 타겟 수
    """

    def __init__(self, num_classes, num_regression_targets):
        super().__init__()

        # ResNet34 백본 (사전학습 가중치 없음)
        resnet = models.resnet34(weights=None)
        self.features = nn.Sequential(*list(resnet.children())[:-1])

        # 분류 헤드
        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Dropout(0.5),
            nn.Linear(512, 256),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(256, num_classes)
        )

        # 회귀 헤드
        self.regressor = nn.Sequential(
            nn.Flatten(),
            nn.Dropout(0.5),
            nn.Linear(512, 384),
            nn.ReLU(),
            nn.BatchNorm1d(384),
            nn.Dropout(0.4),
            nn.Linear(384, 256),
            nn.ReLU(),
            nn.BatchNorm1d(256),
            nn.Dropout(0.3),
            nn.Linear(256, num_regression_targets)
        )

    def forward(self, x):
        """
        순전파

        Args:
            x: 입력 이미지 텐서

        Returns:
            (classification_output, regression_output)
        """
        features = self.features(x)
        return self.classifier(features), self.regressor(features)
