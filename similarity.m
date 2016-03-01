matrix = csvread('matrix.csv', 1);
[m,n] = size(matrix);
list = zeros(1,m);

for i = 1:m
    list(i) = list(i) + i;
end

simMatrix = squareform(pdist(matrix, 'euclidean'));

newM = zeros(m);
for j = 1:m
    tmp = [simMatrix(j,:);list];
    sortTmp = (sortrows(tmp',1))';
    newM(j,:) = sortTmp(2,:);
end
csvwrite('euclidean.csv', newM);

simMatrix = squareform(pdist(matrix, 'cosine'));
newM = zeros(m);
for j = 1:m
    tmp = [simMatrix(j,:);list];
    sortTmp = (sortrows(tmp',1))';
    newM(j,:) = sortTmp(2,:);
end
csvwrite('cosine.csv', newM);

simMatrix = squareform(pdist(matrix, 'jaccard'));
newM = zeros(m);
for j = 1:m
    tmp = [simMatrix(j,:);list];
    sortTmp = (sortrows(tmp',1))';
    newM(j,:) = sortTmp(2,:);
end
csvwrite('jaccard.csv', newM);
