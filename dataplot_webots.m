clc; clear; close all;

%% ================= USER-DEFINED SETTINGS =================
FIGURE_NAME = 'MFASMC Wall-Following Performance';

FIGURE_SIZE = [100 100 1200 800];   % [x y width height]

FONT_SIZE = 21;
FONT_NAME = 'Times New Roman';

TIME_LIMIT = [0 200];

% ---- Legend names (edit freely) ----
LEGEND_LEFT = {'Robot 1','Robot 2','Robot 3','Reference Trajectory'};
LEGEND_XI   = {'\Xi_1','\Xi_2','\Xi_3'};

% ---- Line styles & colors (edit freely) ----
LINE_WIDTH = 1.8;

COLORS = [ ...
    0.00 0.45 0.74;   % blue
    0.85 0.33 0.10;   % orange
    0.47 0.67 0.19;   % green
];

REF_COLOR = [0 0 0];   % black
REF_STYLE = '--';

%% ================= DATA FILES =================
dataFolder = 'Dataplot';
dataFiles = { ...
    fullfile(dataFolder, 'robot1_mfasmc_data.csv'), ...
    fullfile(dataFolder, 'robot2_mfasmc_data.csv'), ...
    fullfile(dataFolder, 'robot3_mfasmc_data.csv') ...
};

%% ================= READ DATA =================
t_data = cell(1,3);
left_data = cell(1,3);
xi_data = cell(1,3);
desired_data = [];

for k = 1:length(dataFiles)
    T = readtable(dataFiles{k});
    t_data{k} = T{:,1};
    left_data{k} = T{:,2};
    xi_data{k} = T{:,5};
    if isempty(desired_data)
        desired_data = T{:,6};
    end
end

%% ================= CREATE FIGURE =================
%% ================= FIGURE 1: CONSENSUS TRACKING =================
figure('NumberTitle','off', ...
       'Position',FIGURE_SIZE);

for k = 1:3
    ax = subplot(3,1,k); hold on;

    % Robot trajectory
    plot(t_data{k}, left_data{k}, ...
        'LineWidth', LINE_WIDTH, ...
        'Color', COLORS(k,:), ...
        'DisplayName', LEGEND_LEFT{k});

    % Reference trajectory
    plot(t_data{k}, desired_data, ...
        'LineStyle', REF_STYLE, ...
        'Color', REF_COLOR, ...
        'LineWidth', LINE_WIDTH, ...
        'Marker','o',...
        'MarkerSize', 3, ...
        'MarkerIndices', 7:25:length(t_data{k}), ...
        'DisplayName', 'Reference');

    ylabel(['Robot ', num2str(k), ' Distance (cm)'], ...
        'FontSize', FONT_SIZE, ...
        'FontName', FONT_NAME);

    xlim(TIME_LIMIT);


    if k == 3
        xlabel('Time (s)', ...
            'FontSize', FONT_SIZE, ...
            'FontName', FONT_NAME);
    end

    legend('show', ...
        'FontSize', FONT_SIZE-3, ...
        'FontName', FONT_NAME, ...
        'Location','best');

    set(ax, ...
        'FontSize', FONT_SIZE, ...
        'FontName', FONT_NAME, ...
        'LineWidth', 1.2);
end
