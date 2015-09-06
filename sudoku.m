function [] = sudoku()

filename = 'game6.txt';

%test_conversion(); return;

% load game
fd = fopen(filename, 'r');
assert(fd ~= 0);
[hints, bmap] = loadgame(fd);
cmat = init_cmat();

%test_constraint(cmat);

% pprint(bmap);
% 
[cmat, bmap, nleft] = singleton_sweep(cmat, bmap, hints);

if nleft == 0
    return;
end

fprintf('\nSweep result\n');
pprint(bmap);

fprintf('%d more spots to solve.\n', nleft);

% If the simple solver did not solve the problem, invoke 2nd stage
active_rows = find(sum(cmat, 2)); % collapse columns
active_cols = find(sum(cmat, 1)); % collapse rows
    
cmat = cmat(active_rows, :);
cmat = cmat(:, active_cols);

% x = solve_primal(cmat);
x = solve_linprog(cmat);
for i = 1:numel(x)
    idx = active_cols(i);
    [r, c, l] = ind2rcl(idx);
    bmap(r,c,l) = x(i);
end

% 
% bmap = secret_souce(cmat);
% 
fprintf('Final result\n');
pprint(bmap);
if validate_solution(bmap)
    fprintf('Solution is validated.\n');
end

end

function test_conversion()

n = 10;
rng(0);
list = randi(9,n,3);

comp = zeros(n, 6);
for i=1:n
   r = list(i,1); c = list(i,2); l = list(i,3);
   
   ind = rcl2ind(r,c,l);
   
   [rc, cc, lc] = ind2rcl(ind);
   comp(i,:) = [rc, cc, lc, list(i,:)];
end

end

function test_constraint(Cmat)

n = 1;
list = (randi(9,n,3));

for i=1:n
    r = list(i,1); c=list(i,2); l=list(i,3);
    
    ind = rcl2ind(r,c,l);
    nz_r = find(Cmat(:,ind));
    [~, nz_c] = find(Cmat(nz_r, :));
    nz_c = unique(nz_c);
    
    [rz, cz, lz] = ind2rcl(nz_c);
    
    a = [r c, l; rz cz lz]'
end

end

function [flag] = validate_solution(bmap)

flag = 1;
% Check level wise:
lev_map = sum(bmap, 3);
lev_invalid = find(lev_map ~= 1);
if numel(lev_invalid) ~= 0
    fprintf('Level check failed.\n');
    flag = 0;
end

% Check col wise:
col_map = sum(bmap, 2);
col_invalid = find(col_map ~= 1);
if numel(col_invalid) ~= 0
    fprintf('Column check failed.\n');
    flag = 0;
end

% Check row wise:
row_map = sum(bmap, 2);
row_invalid = find(row_map ~= 1);
if numel(row_invalid) ~= 0
    fprintf('Row check failed.\n');
    flag = 0;
end

for br=1:3:9
   for bc=1:3:9
       box = sum(sum(bmap(br:br+2, bc:bc+2, :), 1), 2);
       box_invalid = find(box ~= 1);
       if numel(box_invalid) ~= 0
          fprintf('Box check failed.\n');
          flag = 0;
       end
   end
end

end

function [sol] = solve_linprog(cmat)
[m, n] = size(cmat);

f = [zeros(n,1); ones(n,1)];
A = [eye(n) -eye(n); -eye(n) zeros(n)];
b = zeros(2*n, 1);
Aeq = [cmat zeros(m, n)];
beq = ones(m, 1);
option = optimoptions('linprog','Algorithm','dual-simplex','Display','iter')

[x, fval] = linprog(f, A, b, Aeq, beq, [], [], [], option);

sol = round(x(1:n));
end

function [x] = solve_primal(A)
[m, n] = size(A);
b = ones(m,1);

cvx_begin
    variable x(n)
    minimize(norm(x, 1))
    subject to 
        A*x == b;
cvx_end

x = round(x);

% for i=1:n
%    [row, col, lev] = ind2rcl(i);
%    
%    bmap(row, col, lev) = sprintf('%.0f', x(i));
% end
end

function [cmat, bmap, nleft] = singleton_sweep(cmat, bmap, hints)
    
% rows_todie = []; % these are rows and cols in cmat, not to be 
% cols_todie = []; % confused with (row, col, lev) which are for bmap
nleft = 81;

while numel(hints) > 0
    % Pop the first entry from the hint list
    idx = hints(1); %rcl2ind(row, col, lev);
    hints(1) = [];
    nleft = nleft - 1;
        
    % For all rows where the idx col is 1:
    nz_r = find(cmat(:,idx));

    % Find all cols that are zero-ed out but the hint
    % (including the hint column itself)
    [~, nz_c] = find(cmat(nz_r, :));
    nz_c = unique(nz_c);
    cmat(:, nz_c) = 0;
    
    % Update bmap
    for i = 1:numel(nz_c)
        nz_col = nz_c(i);
        [r, c, l] = ind2rcl(nz_col);
        if nz_col == idx
%            fprintf('\n(%d %d %d)\n', r, c, l);
            bmap(r, c, :) = 0; % set all but l to 0
            bmap(r, c, l) = 1;
        else
            bmap(r, c, l) = 0;
        end
    end
    
%     rows_todie = unique([rows_todie; nz_r]);
%     cols_todie = unique([cols_todie; nz_c]);
    
    if numel(hints)==0
        singleton_rows = find(sum(cmat, 2)==1);
        [~, singleton_cols] = find(cmat(singleton_rows,:));
        singleton_cols = unique(singleton_cols);
        hints = singleton_cols;
    end
    
%    pprint(bmap);
end

end

function [row, col, lev] = ind2rcl(ind)
%     lev = mod(ind-1, 9)+1;
%     row = floor(ind/81)+1;
%     col = floor(mod(ind,81)/9)+1;
    row = mod(ind-1, 9)+1;
    col = floor(mod(ind-1,81)/9)+1;
    lev = floor((ind-1)/81)+1;
end

function [ind] = rcl2ind(row, col, lev)
%    ind = (row-1)*81 + (col-1)*9 + lev;
    ind = row + (col-1)*9 + (lev-1)*81;
end

function [cmat] = init_cmat()
cmat = zeros(4*9*9, 9*9*9);

c_count = 1;
% Row constraints
for c=1:9
    for l=1:9
        cmat(c_count, rcl2ind(1:9, c, l)) = 1;
        c_count = c_count+1;
    end
end

% Column constraints
for r=1:9
    for l=1:9
        cmat(c_count, rcl2ind(r, 1:9, l)) = 1;
        c_count = c_count+1;
    end
end

% Level constraints
for r=1:9
    for c=1:9
        cmat(c_count, rcl2ind(r, c, 1:9)) = 1;
        c_count = c_count+1;
    end
end

for l=1:9
    for r=1:3:9
        for c=1:3:9
            cmat(c_count, rcl2ind(r  , c:c+2, l)) = 1;
            cmat(c_count, rcl2ind(r+1, c:c+2, l)) = 1;
            cmat(c_count, rcl2ind(r+2, c:c+2, l)) = 1;
            c_count = c_count+1;
        end
    end
end

end

function [hints, bmap] = loadgame(fd)
hints = [];
bmap = ones(9,9,9);

for i=1:9
    for j=1:9
        char = fscanf(fd, ' %c', 1);
        if char ~= '.'
            l = char-'0';
            hints = [hints; rcl2ind(i, j, l)];
            bmap(i, j, :) = 0;
            bmap(i, j, l) = 1;
        end
    end
end
end

function [] = pprint(bmap)

% Find the maximum width we have to deal with
width = max(max(sum(bmap, 3)));
fmt = ['%', sprintf('%d', width), 's'];

line = repmat('-', 1, 3*(width+1));
for i = 1:9
    if i == 4 || i == 7
        fprintf('%s+%s+%s\n', line, line, line);
    end
    
    for j=1:9
        num = '';
        for k=1:9
            if bmap(i,j,k)
                num = sprintf('%s%d', num, k);
            end
        end
        fprintf('%s',strjust(sprintf(fmt, num),'center'));
        
        if j== 3 || j== 6
            fprintf(' |');
        elseif j==9
            fprintf('\n');
        else
            fprintf(' ');
        end
    end
end
end %pprint